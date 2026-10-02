# Learnings inbox

The live queue. New candidates go at the top. Format: `TEMPLATE.md`.
Curation rules: `planning/v1-redefinition/learning-lifecycle.md`.

Statuses: `candidate` → `evidence-gathering` → `promoted` / `retained` /
`merged:<id>` / `discarded`.

---

### L-082 — the three-stage comparative-trial structure (discovery/design → evaluator-sufficient evaluation → evaluator-gated optional implementation check) works cleanly on its first real exercise

- **origin:** Phase 78 (Priority A backlog rationalisation + second
  Ledgerkit validation trial)
- **date:** 2026-10-02
- **project_revision:** `7e4907c`
- **observation:** Phase 78's plan (second revision) restructured an
  originally confounded "design-and-implement independently, then
  compare" trial design into three explicit stages specifically to
  prevent differing implementation choices being mistaken for differing
  context quality: Stage 1 (discovery/design comparison only, no code),
  Stage 2 (an independent evaluation sufficient on its own to decide the
  exit question), and an optional Stage 3 (a shared, human-approved
  implementation contract) whose go/no-go is explicitly the Stage 2
  evaluator's own call, never the lead's. On this first real run, the
  evaluator declined Stage 3 with a specific, evidenced reason (the
  `CG-001` question was already decisively answered by Stage 2's own
  independent re-derivation; the remaining open questions from Stage 1
  were product-design uncertainties unrelated to CodeCompass's own
  availability) rather than defaulting to running it "to be thorough" —
  the delegation worked as designed, not just in principle.
- **evidence:**
  `planning/reference-projects/ledgerkit/06-stage-d-reportspec-priority-a-validation.md`'s
  own "Stage 3 decision" section; cross-checked independently by the
  separate `knowledge-curator` §7.2 triage
  (`planning/reference-projects/ledgerkit/06-priority-a-exit-decision-triage.md`),
  which reviewed the same evidence and reached the same conclusion via a
  different evidence path (direct schema/code re-reading plus both
  agents' own contemporaneous research traces) rather than simply
  trusting Stage 2's own report.
- **classification:** workflow
- **status:** retained
- **recurrence:** first occurrence of this specific three-stage structure
  being run for real (it was designed, not yet exercised, at the time
  Phase 78's plan was amended).
- **moves forward when:** a future comparative CodeCompass-advantage
  trial (any reference project, any task) adopts this three-stage shape
  as its own default template rather than re-deriving a trial structure
  from scratch each time.
- **curation (this triage, 2026-10-02, knowledge-curator):** **retain**,
  not promote. The observation is real and the evidence genuinely
  independent (two separate verification paths converged, per the
  entry's own evidence field) — but it is a confirmation of a design
  that was itself only just exercised for the first time this phase.
  The entry's own "moves forward when" condition ("a future comparative
  trial adopts this three-stage shape as its own default template") has
  not yet happened; one successful run is evidence the shape *can* work,
  not yet evidence it has become this project's default. Promoting a
  single-instance confirmation into `reference-project-protocol.md` or
  `context-quality-evaluation.md` as a named default template now would
  be writing a rule from n=1, before a second trial has had the chance
  to either confirm the pattern or surface a case where the three-stage
  split doesn't fit as cleanly. Leave as a retained candidate: the next
  comparative CodeCompass-advantage trial (reference project, any task)
  should explicitly consider reusing this shape, and if it does (or
  deliberately doesn't, for a stated reason), that's the recurrence this
  candidate needs to become promotable — most naturally into
  `planning/v1-redefinition/context-quality-evaluation.md` (where the
  comparative-trial methodology already lives, e.g. `L-027`'s
  single-trial-variance caveat) or `reference-project-protocol.md` §2.4
  (the per-task procedure), whichever a future curator judges the better
  fit once there's a second data point to generalise from.

### L-081 — for a reference-project trial with no Anthropic API key configured, use `codecompass --budget 0` directly, not `--yes`

- **origin:** Phase 78 (Priority A backlog rationalisation + second
  Ledgerkit validation trial), treatment-clone setup
- **date:** 2026-10-02
- **project_revision:** `bd8f48c`
- **observation:** running bare `codecompass --yes` in the Ledgerkit
  treatment scratch clone (zero third-party dependencies tracked)
  attempted real AI-enrichment calls for 388 doc-relationship mentions
  (enrichment is not gated on vendor count — zero tracked vendors does
  not imply zero enrichment candidates) and failed with an unrelated-
  looking Anthropic SDK error (`TypeError: "Could not resolve
  authentication method..."`) before ever reaching the actual, intended
  budget-estimate message. Re-running with `--budget 0` instead produced
  the real, informative message directly ("estimated cost $0.16 for 8
  batch(es)... exceeds --budget $0.00") and the deterministic graph
  rebuild (first-party source/symbol indexing, the generated `.claude/`
  artifacts) completed successfully regardless, since enrichment is a
  separate, later pipeline step that aborting does not block.
- **evidence:** direct reproduction during Phase 78's own treatment-clone
  setup — first attempt (`--yes`) failed with the SDK error; second
  attempt (`--budget 0`) succeeded with the graph rebuild intact and a
  clean, correctly-worded budget-exceeded message.
- **classification:** workflow
- **status:** promoted
- **recurrence:** first occurrence noticed; the underlying condition
  (enrichment cost estimation runs regardless of tracked-vendor count,
  and `--yes` alone does not cap spend) is a standing, mechanical fact
  about `codecompass`'s own bootstrap sequence, not a one-off fluke — so
  this will recur identically for any future reference-project dispatch
  run without a configured API key.
- **moves forward when:** a future reference-project trial's own setup
  instructions default to `--budget 0` for any dispatch environment
  without a configured Anthropic API key, rather than `--yes`.
- **curation (this triage, 2026-10-02, knowledge-curator):** **promote**.
  This is a concrete, evidenced, mechanical fact about CodeCompass's own
  bootstrap sequence (not an opinion about process), it will recur
  identically for any future reference-project dispatch run without a
  configured API key (per the entry's own recurrence note), and a future
  dispatch-setup step is exactly where a reader needs it *before* hitting
  the same failed attempt — the same shape `L-046`'s credential-probe
  paragraph and `L-080`'s commit-message paragraph already have in
  `planning/agent-led-workflow.md` step 6. This candidate, though, is
  specific to *reference-project trial* scratch-clone setup, not general
  implementation work — `planning/v1-redefinition/reference-project-protocol.md`
  §2.2 ("Working copy discipline," the section that already covers
  "CodeCompass is run against that clone from CodeCompass's installed
  CLI") is the better-fitting destination, matching the precedent of
  `L-022` and `L-062`, both already landed in this same section.
  **Destination:** `planning/v1-redefinition/reference-project-protocol.md`
  §2.2, added paragraph (drafted below). Outside this curator's own write
  scope, so landing it is the lead's action — append after the existing
  `L-062` paragraph in §2.2:

  > **Added 2026-10-02 (`L-081`, Phase 78):** when bootstrapping a
  > reference-project scratch clone in a dispatch environment with no
  > Anthropic API key configured, run `codecompass --budget 0` (or a
  > small explicit cap) directly — **not** `codecompass --yes`. `--yes`
  > does not itself cap AI-enrichment spend, and doc-relation enrichment
  > cost estimation runs regardless of tracked-vendor count (zero
  > third-party dependencies does not imply zero enrichment candidates —
  > doc-relationship *mentions* are what's estimated, not vendor count).
  > Bare `--yes` therefore still attempts real enrichment calls and fails
  > with an unrelated-looking Anthropic SDK authentication error
  > (`TypeError: "Could not resolve authentication method..."`) before
  > ever reaching the real, intended budget-gate message. `--budget 0`
  > reaches that message directly ("estimated cost $X for N
  > batch(es)... exceeds --budget $0.00") and the deterministic graph
  > rebuild (first-party source/symbol indexing, generated `.claude/`
  > artifacts) completes successfully regardless, since enrichment is a
  > separate, later pipeline step that aborting does not block. Confirmed
  > at Phase 78: the Ledgerkit treatment scratch clone's first sync
  > attempt (`--yes`) failed this way; the second (`--budget 0`)
  > succeeded cleanly.

  **Landed**: `planning/v1-redefinition/reference-project-protocol.md`
  §2.2, appended after the `L-062` paragraph. `promoted.md` pointer line
  added.

### L-080 — never construct a multi-line `git commit -m` message containing backtick-quoted code identifiers as an interpolated shell string

- **origin:** Phase 80 (CodeCompass-wide documentation reconstruction),
  Part 4 verification commit
- **date:** 2026-10-02
- **project_revision:** `3bfcc4d` (corrupted), amended to `33bc68a`
  (corrected, not yet pushed at time of amend)
- **observation:** a multi-line commit message containing backtick-
  quoted code identifiers (e.g. `` `codecompass query source-stats` ``)
  was passed to `git commit -m` as an interpolated shell string. The
  backticks were interpreted as command substitution before `git`
  itself ever saw the text — the enclosed span was executed as a real
  shell command (a genuine CLI invocation in this project's own venv,
  which failed with a Typer usage error) and the commit landed with that
  span silently replaced by the failed command's own stderr text,
  instead of the intended words.
- **evidence:** `git log -1 --format=%B` immediately after the commit
  showed the corrupted span directly; confirmed the cause by noting the
  missing text was exactly the one backtick-quoted phrase in that
  paragraph, and that the stray output matched a real Typer "Missing
  command" error for the literal command the backticked text would
  execute if run.
- **classification:** workflow — scoped to this project's own
  session/git practice (`planning/agent-led-workflow.md`), not
  project-rule/`CLAUDE.md`-tier. Retains the filer's own correct call
  that this is a Claude Code tool-usage pitfall, not a CodeCompass
  development-process rule in the `CLAUDE.md` §1/§5 sense — but "not
  CLAUDE.md-tier" and "not this project's queue at all" are different
  claims, and only the first is true (see curation note).
- **status:** promoted
- **recurrence:** first occurrence noticed; the same construction
  (interpolated `-m` string with backtick-quoted code) had very likely
  been used safely many times earlier in this same phase purely by
  chance (no command-shaped backtick content happened to appear) — this
  is a latent risk in an established habit, not a one-off slip.
- **moves forward when:** a future commit-message construction habit
  change — e.g. routing every multi-line, backtick-containing commit
  message through `git commit -F <file>` instead of an interpolated
  `-m` string — can cite this as the concrete, evidenced reason. Also
  filed as Claude-Code product feedback (not duplicated here as a
  CodeCompass rule, since the fix belongs in session habits, not this
  project's own files).
- **curation (this triage, 2026-10-02, knowledge-curator):** **promote
  (narrow)** — not discard. The entry's own classification is right that
  this isn't `CLAUDE.md`/project-rule material, and it's reasonable that
  it was separately filed as Claude Code product feedback — but that
  filing addresses the *tool's* underlying shell-quoting behavior, which
  is out of this project's control either way. It doesn't address this
  project's own concrete, recurring exposure: this repo's commit
  convention (`CLAUDE.md` §6, `type(phase-N): summary`) and its own
  practice of citing code/CLI identifiers in backticks inside commit
  bodies (visible throughout `planning/learnings/promoted.md`'s own
  pointer lines and this phase's own corrupted commit) make the specific
  precondition for this failure — a backtick-quoted identifier inside a
  multi-line `-m` string — a routine occurrence in *this* repo, not an
  edge case. Whether or not Claude Code's own product behavior ever
  changes, a future session working in this exact repo benefits from a
  standing habit, independent of the product-feedback outcome. Scoped
  narrowly (one short paragraph, no new process), not promoted to
  `CLAUDE.md` per the entry's own correct scoping call.

  **Destination:** `planning/agent-led-workflow.md` step 6 (implementation
  step — the existing `L-046` credential-probe paragraph is embedded in
  this exact step already, same "a concrete tooling pitfall discovered
  mid-phase" shape). Outside this curator's own write scope, so landing
  it is the lead's action. Draft paragraph, ready to append after the
  existing `L-046` paragraph in step 6:

  > **Before running `git commit -m` with a multi-line message that
  > contains backtick-quoted code identifiers (e.g. `` `codecompass query
  > source-stats` ``), write the message to a file and use
  > `git commit -F <file>` instead.** An interpolated `-m` shell string
  > executes backtick-enclosed spans as command substitution before `git`
  > ever sees the text, silently replacing that span with whatever the
  > resulting (likely failing) command printed to stderr — not a `git`
  > error, so nothing stops the commit from landing corrupted. Confirmed
  > at Phase 80 (`L-080`): a real commit landed with a backtick-quoted CLI
  > phrase replaced by a failed Typer invocation's own error text, caught
  > only by reading the commit back immediately with
  > `git log -1 --format=%B` and fixed via `git commit --amend -F <file>`
  > before it reached `origin`. Reading a just-made commit back this way
  > remains good practice regardless.

  **Landed**: `planning/agent-led-workflow.md` step 6, appended after the
  `L-046` paragraph. Status flipped to `promoted`; `promoted.md` pointer
  line added.

### L-079 — documentation-accuracy and coding-context-advantage checks are not substitutes for each other, even run back-to-back through the same pipeline, because their own ground truth operates at different levels of detail

- **origin:** Phase 80 (CodeCompass-wide documentation reconstruction),
  Part 4 verification
- **date:** 2026-10-02
- **project_revision:** `33bc68a`
- **observation:** a bounded coding-context packet built from this
  phase's own frozen snapshot and model-blind reconstruction contained a
  real, consequential factual error (a conflation of two distinct graph-
  opening helper functions, `_open_graph_or_note`/`_graph_session` vs.
  the actually-used `_open_graph_if_exists`, plus an invented NULL-value
  label inconsistent with the real, already-established one). This error
  originated in the Stage 2 reconstruction's own summary prose and
  **survived two independent checks untouched**: Stage 3's comparison
  (against the frozen snapshot's own Claims, which are conceptual/
  meta-level and never described CLI-helper-naming at this granularity)
  and Stage 5's reconciliation (against the real published docs, which
  — correctly, for their own audience — also never state this
  implementation-level detail either way). The error was invisible to
  both checks not because either was performed carelessly, but because
  neither check's own evidentiary scope covered this level of detail. It
  only surfaced when the packet was independently evaluated against raw
  source by `context-evaluator`, for its own, separate, intended
  purpose.
- **evidence:** `planning/phase-80-docs-draft/_part4-coding-context-packet-evaluation.md`
  — full root-cause trace, FAIL verdict, LOW advantage rating, with
  direct `cli.py`/`graph.py` line citations for both the error and the
  correct behavior.
- **classification:** workflow (normalized from the filer's own
  "process/methodology principle" to the nearest §3 canonical value,
  since the destination is a methodology-spec ground rule, same tier as
  `L-027`/`L-062`/`L-074`, not an ADR or architecture doc).
- **status:** promoted
- **recurrence:** first occurrence this specific error shape; the
  general pattern ("a check's own scope has a blind spot one level more
  granular than what it compares against") echoes `L-075`'s "scope vs.
  depth" distinction from a different lineage (fail-closed validation),
  suggesting this may be a recurring shape worth a shared principle
  rather than two independent one-off learnings, if it recurs again in a
  third context.
- **moves forward when:** a future phase considers merging or
  sequencing documentation-accuracy and coding-context-advantage checks
  for efficiency — this learning is the evidenced reason to keep them
  separate and both mandatory, not optional belt-and-suspenders.
- **curation (this triage, 2026-10-02, knowledge-curator):** **promote**
  — provenance accepted (all required fields present once classification
  normalized above). Independently re-read
  `planning/phase-80-docs-draft/_part4-coding-context-packet-evaluation.md`
  directly: it confirms the FAIL/LOW verdict, the specific helper-function
  conflation (`_open_graph_or_note`/`_graph_session` vs. the real
  `_open_graph_if_exists`), and traces the error's survival through
  Stage 3 and Stage 5 exactly as this entry states — a real, concrete,
  single-instance-but-costly finding, not a hypothetical.

  **Checked the proposed `L-075` merge/link first, since the entry itself
  raises it.** Decision: **do not merge** — these are related but
  distinct failure shapes, not one recurrence of the other. `L-075`
  describes a *single* check that correctly widened its own scope but
  left one axis (value-depth) of *that same check* shallow. `L-079`
  describes *two separate, each-individually-correct* checks
  (documentation-accuracy, coding-context-advantage) that were never
  designed to cover the same granularity in the first place — nothing
  about either check is shallow or incomplete on its own terms; the gap
  exists only in the space between them. Cross-linking both as "the
  general shape of 'a check's designed scope has a boundary, and an
  error can hide exactly past that boundary' recurs across unrelated
  lineages" is worth a shared one-line pointer, but a merge would
  misleadingly collapse "fix this one checker's depth" (L-075's actual
  remedy) with "never collapse these two whole evaluation tracks into
  one" (L-079's actual remedy) into a single recurrence count neither
  remedy satisfies alone.

  **Destination:** `planning/v1-redefinition/context-quality-evaluation.md`
  §1 "Ground rules" — the same file/section `L-027` and the Phase 61
  single-trial-comparison ground rule already landed in, for the same
  reason (a design-level pitfall in how the evaluation pipeline itself is
  run, applicable to every future phase that runs both checks, not just
  Phase 80's own). This is outside this curator's own write scope
  (`planning/v1-redefinition/**` is not in the allowed-write list), so
  landing it is the lead's (or `docs-maintainer`'s) action, not mine.
  Draft ground-rule bullet, ready to append to §1 after the existing
  `L-062`/Phase 75 cross-reference bullet:

  > - **A documentation-accuracy check and a coding-context-advantage
  >   check are not substitutes for each other, even when both compare
  >   against the same frozen snapshot/reconstruction materials.** Their
  >   own evidentiary standards operate at different levels of
  >   granularity — a documentation-accuracy comparison's ground truth is
  >   published, conceptual prose (a Claim, a README paragraph); a
  >   coding-context-advantage evaluation's ground truth is literal,
  >   implementation-level call-site behaviour (the actual helper function
  >   invoked, its actual signature). An error below the documentation
  >   check's own granularity can cleanly survive a correct, careful
  >   documentation-accuracy comparison and still mislead an implementer,
  >   because neither check was ever scoped to catch it. Confirmed at
  >   Phase 80 (`L-079`): a coding-context packet's own real
  >   helper-function conflation survived both the model-blind
  >   reconstruction's comparison against the frozen snapshot's Claims and
  >   reconciliation against the real published docs untouched, and was
  >   only caught when the packet was evaluated, separately and for its
  >   own stated purpose, against raw source. Do not merge, skip, or
  >   sequence-and-shortcut one of these two checks on the assumption that
  >   passing the other makes the other redundant.

  **Landed**: `planning/v1-redefinition/context-quality-evaluation.md`
  §1 "Ground rules", appended after the `L-062` cross-reference bullet.
  Status flipped to `promoted`; `promoted.md` pointer line added.

### L-078 — a post-`done` corrective amendment to an already-implemented, reconciled phase gets a new numbered ADR in the same lineage, not an in-place edit — now confirmed repeatable, not a one-off

- **origin:** Phase 79 (clean-room conceptual understanding + documentation
  reconstruction), sixth amendment / `decisions/0068` "Consequences"; retro
  "Governing-ADR lineage note"; filed at this triage's own initiative per
  the retro's own explicit question ("worth watching whether this becomes
  a recurring pattern worth a named process note"), deferring the
  promote/retain/discard decision to `knowledge-curator` per usual
  practice.
- **date:** 2026-10-01
- **project_revision:** `94f1e51`
- **observation:** `decisions/0067` first reasoned that the fifth
  amendment's corrections to the fourth revision's `done`-flipped,
  already-executed result belonged in a *new* numbered ADR
  (`decisions/0067`) rather than a further in-place edit to
  `decisions/0066`, specifically because `0066` had "already informed
  real, executed, `done`-flipped work" — editing it further would quietly
  rewrite the historical record of what was decided under what
  understanding at the time. The sixth amendment applied the identical
  reasoning a second time: `decisions/0067`'s own corrections had
  themselves since been implemented, independently re-audited, and
  terminally reconciled, so the sixth amendment's three further
  corrections went into a new `decisions/0068` rather than a further edit
  to `0067`. This is now a two-instance lineage
  (`0066` → `0067` → `0068`) of the identical pattern — a post-`done`
  corrective amendment to a phase always produces a new numbered ADR, by
  the same append-only reasoning `CLAUDE.md` §2 already states for ADRs
  generally, but applied specifically to the narrower case of *correcting
  an already-reconciled phase's own prior correction*. `decisions/0068`'s
  own "Consequences" section already draws this conclusion explicitly:
  "the pattern `0067` established... is confirmed as a repeatable one,
  not a one-off... A future phase in the same situation can cite this
  precedent directly rather than re-deriving it from `CLAUDE.md` §2's more
  general wording."
- **evidence:** `decisions/0067` "Alternatives considered" (the original
  reasoning for not editing `0066` in place); `decisions/0068` "Decision"
  ("By the exact same reasoning `0067` applied to `0066`") and
  "Consequences" (the explicit "confirmed as a repeatable one... second
  application" language, quoted above); `planning/phase-79-clean-room-understanding-and-documentation-reconstruction.md`
  line 38-46 ("Governing ADR lineage: `decisions/0066`... →
  `decisions/0067`... → `decisions/0068`... each new ADR rather than a
  further in-place edit, per `0067`'s own established reasoning");
  `planning/retros/phase-79-clean-room-understanding-and-documentation-reconstruction.md`
  "Governing-ADR lineage note" (independently re-read directly — matches
  the ADR/plan account exactly, including the explicit "worth watching
  whether this becomes a recurring pattern" framing).
- **classification:** workflow
- **status:** promoted
- **recurrence:** second application of the identical reasoning within
  one phase's own lineage (`0066`→`0067` established it; `0067`→`0068`
  confirmed it) — meets this project's own recurrence bar for codifying a
  process note, though both instances are within a single phase (the same
  caveat `L-070`'s own curation note raised and accepted for its own
  two-instance, single-phase recurrence).
- **promoted_to:** `planning/v1-redefinition/agent-led-development.md` Sec 1 "Principles," new bullet after the existing "An agent observation is not authoritative..." bullet @ (this phase's own closeout commit)
- **curation (this triage, 2026-10-01, knowledge-curator):** provenance
  accepted — all required fields present (filed fresh at this triage,
  per the retro's own explicit question rather than a prior candidate
  naming). Independently re-read `decisions/0067`'s "Alternatives
  considered," `decisions/0068`'s "Decision"/"Consequences," the plan's
  own lineage line, and the retro's "Governing-ADR lineage note" directly
  — all four agree exactly on the mechanism (a new ADR per post-`done`
  correction) and the explicit "confirmed as repeatable" framing.

  Checked for a merge/duplicate candidate: grepped this inbox for
  "ADR lineage," "in-place edit," "append-only" — no prior candidate
  addresses this specific pattern (when a *post-`done` corrective
  amendment* gets its own new ADR vs. editing the prior one). Distinct
  from `CLAUDE.md` §2's own general ADR append-only rule (which already
  covers "a reversed decision gets a new numbered file") — this candidate
  is narrower and more specific: it is about an ADR that was never
  reversed, only further corrected after its own content had already
  shipped, a case `CLAUDE.md` §2's existing wording doesn't explicitly
  name. Checked whether this belongs in `context-gaps/` or
  `context-observations/` instead: no to both — this is not a
  relationship CodeCompass's own graph is missing, nor an experience with
  an existing graph edge; it is a documentation-governance convention for
  this project's own ADR-authorship practice, so it correctly stays in
  `planning/learnings/`.

  **Outcome: promote (recommendation + draft; does not land here — the
  recommended destination, `planning/v1-redefinition/agent-led-development.md`,
  is outside this agent's write boundary).** Real, specific, and already
  self-identified by `decisions/0068`'s own "Consequences" section as
  worth a standing citation point for a future phase — the retro's own
  question ("worth a named process note... rather than something
  re-derived fresh each time") is itself the strongest argument for
  promoting now rather than waiting for a third instance: the whole point
  of naming the pattern is to let a future phase cite it directly instead
  of re-deriving `0067`'s reasoning from `CLAUDE.md` §2's more general
  wording a third time. Classified `workflow` (a repeatable
  project-process pattern, not a new rule imposed on agent behavior)
  rather than `project-rule`/`CLAUDE.md`, since this doesn't change what
  any agent or the lead is required to do differently — `CLAUDE.md` §2's
  append-only ADR rule already covers the underlying requirement; this is
  a named-precedent note for the planning doc that already describes how
  the agent-led model's artifacts relate to each other.

  **Recommended fix — add a new bullet to
  `planning/v1-redefinition/agent-led-development.md` §1 "Principles,"
  after the existing "An agent observation is not authoritative..."
  bullet** (draft, for the lead to review and land; not applied here):

  > **A post-`done` corrective amendment to an already-implemented,
  > independently-reconciled phase gets a new numbered ADR in the same
  > lineage, never a further in-place edit to the ADR that already
  > informed the real, executed work it is correcting** — the same
  > append-only reasoning `CLAUDE.md` §2 states for ADRs generally,
  > applied specifically to this narrower, recurring case. Established at
  > `decisions/0067` (correcting `decisions/0066`'s already-`done`-flipped
  > Phase 79 result) and confirmed as repeatable, not a one-off, at
  > `decisions/0068` (correcting `decisions/0067`'s own already-
  > implemented and reconciled corrections) — a future phase facing the
  > same situation can cite this precedent directly rather than
  > re-deriving it from `CLAUDE.md` §2's more general wording each time.
  > (Phase 79 sixth amendment — L-078.)

  Revisit/withdraw if a third instance of this pattern shows the
  "new ADR every time" convention producing an unwieldy, hard-to-follow
  lineage for a single phase (e.g. four or more ADRs correcting one
  another) — not observed yet (two instances, both still easy to follow
  in sequence), but named as the honest revisit condition.

### L-077 — an explicit instruction to test multiple, meaningfully different scenarios caught the exact bug a narrower exercise missed, unprompted, on first pass — but the independent adversarial-review step still found further scenarios beyond what that instructed pass tried

- **origin:** Phase 79 (clean-room conceptual understanding + documentation
  reconstruction), sixth amendment / `decisions/0068` item 2 (second half);
  retro Addendum 2, bullet 3; filed at this triage's own initiative per
  the addendum's explicit candidate-learning naming, deferring the
  promote/retain/discard decision to `knowledge-curator` per usual
  practice.
- **date:** 2026-10-01
- **project_revision:** `94f1e51`
- **observation:** given the chance to re-run the `tinytodo` workflow
  exercise properly (real commits, full pipeline, independent adversarial
  review), the same fresh research dispatch caught the exact `_next_id`
  reuse bug the original, narrower exercise missed — on its first pass,
  unprompted with the answer. The only material difference in the prompt
  was an explicit instruction to test multiple, meaningfully different
  deletion scenarios rather than one. This is a concrete, worked
  demonstration that much of the original defect was a scoping/
  instruction gap in the research-dispatch prompt, not a fundamental
  limit of what a single research pass can catch. The subsequent
  independent adversarial review — which ran anyway, as part of the full
  pipeline, not skipped because the research pass had already found the
  bug — still mattered: it found eight further scenarios beyond the three
  the research pass itself tried, closing the gap between "got the right
  answer" and "verified there wasn't a different wrong answer nearby."
- **evidence:** `decisions/0068` item 2 ("Independently reproduced and
  disproven... a case the original exercise's own single test never
  exercised"); `planning/phase-79-clean-room-understanding-and-documentation-reconstruction.md`
  §0 "Sixth revision" entry 2 (full technical account); `planning/retros/phase-79-clean-room-understanding-and-documentation-reconstruction.md`
  "Addendum 2: sixth amendment," bullet 3 (independently re-read directly
  — matches the ADR/plan account exactly, including the explicit "eight
  further scenarios beyond the three the research pass tried" figure).
- **classification:** workflow
- **status:** retained
- **recurrence:** first occurrence of this specific demonstration (an
  instructed re-run isolating scoping-vs-fundamental-limitation); directly
  paired with `L-076` (same incident, the diagnosis half) — this entry is
  the *remedy-confirmation* half.
- **promoted_to:** (none yet — see outcome below)
- **curation (this triage, 2026-10-01, knowledge-curator):** provenance
  accepted — all required fields present. Independently re-read the
  retro addendum's bullet 3, `decisions/0068`'s item 2, and the plan's own
  §0 "Sixth revision" entry 2 directly — all three agree on the exact
  mechanism (one changed prompt instruction; eight further scenarios
  found by the independent review beyond the research pass's own three).

  Checked for a merge/duplicate candidate: this is the direct companion to
  `L-076` filed in this same triage pass (the diagnosis of the original
  gap) — not a duplicate of it, since it evidences a different, additional
  claim (the fix actually works, *and* the independent-review step
  remains necessary even after the fix). Not a duplicate of `L-027`
  (single-trial baseline/treatment comparisons can't separate tool
  contribution from diligence variance) — related in spirit (both are
  about what a single trial can and can't tell you) but this entry's
  trial was deliberately controlled (one prompt variable changed, same
  dispatch mechanism) rather than an uncontrolled baseline/treatment
  comparison, so it doesn't inherit `L-027`'s specific confound. Checked
  whether this belongs in `context-gaps/` or `context-observations/`
  instead: no to both — this is not a relationship CodeCompass's own
  graph is missing, nor an experience with an existing graph edge; it is
  a research-methodology/process-design finding, so it correctly stays in
  `planning/learnings/`.

  **Outcome: retain, cross-referenced with `L-076`.** This entry's own
  actionable content (the research-dispatch prompt needs an explicit
  scenario-diversity instruction) is identical to what `L-076` already
  recommends promoting — duplicating the same fix under a second entry
  would double-count one recommendation. What this entry adds *beyond*
  `L-076` is purely evidentiary/confirmatory: (a) proof the fix actually
  works, on first try, for the exact bug it was meant to catch; (b) a
  reaffirmation, not a new rule, that the independent adversarial-review
  step must stay mandatory even when the research-dispatch prompt
  improves — the pipeline already treats independent review as a
  separate, required step (`decisions/0049`'s roster model; `domain-skeptic`'s
  own adversarial-review role), and this finding is evidence *for*
  keeping that design exactly as it is, not evidence of a gap in it. No
  new artifact change is recommended for this half; it is recorded here
  as the supporting evidence for `L-076`'s recommendation and as a
  standing reminder (should a future phase ever propose relying on an
  improved prompt alone and dropping independent review) that the two are
  not substitutes for each other even when the prompt fix is shown to
  work.

  Revisit/withdraw if a future phase's own retain-vs-promote review
  judges this reminder valuable enough to also land as an explicit
  sentence somewhere (e.g. `.claude/agents/domain-skeptic.md` or wherever
  the adversarial-review step is specified) — not recommended now since
  no actual proposal to drop or weaken independent review has ever been
  made in this project; this would be a defense against a hypothetical,
  not an observed, failure.

### L-076 — a clean-room/template research pass's own narrow test coverage was mistaken for completeness a second time within the same exercise lineage, because nothing in its lightweight process explicitly required testing more than one scenario of a negative/invariant claim

- **origin:** Phase 79 (clean-room conceptual understanding + documentation
  reconstruction), sixth amendment / `decisions/0068` item 2 (first half);
  retro Addendum 2, bullet 2; filed at this triage's own initiative per
  the addendum's explicit candidate-learning naming, deferring the
  promote/retain/discard decision to `knowledge-curator` per usual
  practice.
- **date:** 2026-10-01
- **project_revision:** `94f1e51`
- **observation:** the fifth amendment's own downstream exercise evidence
  (`template-usability-exercise/tinytodo-after-adoption/`) asserted that
  `tinytodo`'s `_next_id` guarantees a deleted task's id is "never
  reused" (later narrowed, still wrongly, to "as long as the task list
  hasn't been fully emptied"). The sixth amendment independently
  reproduced and disproved this: deleting whichever task currently holds
  the maximum live id causes the very next `add` to reuse that id, even
  with other, older tasks still present and the list never emptied. The
  original exercise's own single test happened to delete a non-maximum
  id — the one case that doesn't falsify the "never reused" claim — and
  nothing in that exercise's own process (a single research pass, no
  independent adversarial check built into the template's own lightweight
  default path) was positioned to notice the untested case was the one
  that actually mattered. This is the same general failure shape (a
  narrow test mistaken for proof of a general claim) recurring within one
  exercise lineage, now caught a second time by direct review rather than
  by the exercise's own design.
- **evidence:** `decisions/0068` item 2 ("a case the original exercise's
  own single test never exercised (it only ever deleted a non-maximum
  id)"); `planning/phase-79-clean-room-understanding-and-documentation-reconstruction.md`
  §0 "Sixth revision" entry 2 (full technical account, including "the
  specific logical error in the original assertion's own 'Counterexamples'
  reasoning"); `planning/retros/phase-79-clean-room-understanding-and-documentation-reconstruction.md`
  "Addendum 2: sixth amendment," bullet 2 (independently re-read directly
  — matches the ADR/plan account exactly); `.claude/agents/context-researcher.md`
  step 2 ("Run representative examples and edge cases yourself") —
  confirmed this existing guidance is general enough that it did not, by
  itself, prevent this exact mistake, since "representative" does not by
  itself require testing the scenario most likely to falsify a negative
  claim.
- **classification:** scoped-rule
- **status:** promoted
- **recurrence:** second occurrence within this same exercise lineage of
  "a single test's own narrow coverage mistaken for a general proof" (the
  original fourth-revision exercise's mistake; now independently confirmed
  and diagnosed by the sixth amendment's direct review) — structurally
  related to, but a distinct shape from, `L-069` (a hand-curated export's
  mechanical truncation bug, not a test-design gap) and `L-027`
  (single-trial baseline/treatment comparisons, a different confound) —
  not a duplicate of either.
- **promoted_to:** `.claude/agents/context-researcher.md` step 2, new sentence after "Run representative examples and edge cases yourself" @ (this phase's own closeout commit)
- **curation (this triage, 2026-10-01, knowledge-curator):** provenance
  accepted — all required fields present. Independently re-read the
  retro addendum's bullet 2, `decisions/0068`'s item 2, and the plan's own
  §0 "Sixth revision" entry 2 directly — all three agree exactly, and I
  separately opened `.claude/agents/context-researcher.md` to confirm its
  existing step 2 guidance ("run representative examples and edge cases
  yourself") does not already explicitly require testing the scenario
  most likely to falsify a negative/invariant claim specifically — it
  does not; the wording is general enough that this exact mistake was
  still possible under it.

  Checked for a merge/duplicate candidate: grepped this inbox for
  "tinytodo," "_next_id," "never reused," "single test," "narrow test
  coverage" — no prior candidate addresses this. `L-021` (CLAUDE.md §1,
  a narrow-scope test isn't sufficient when a real call site exists) and
  `L-074` (a link-check isn't a substitute for a real usability exercise)
  are related in the same general family ("a cheap/narrow check creates
  false confidence") but address different artifacts and different
  failure shapes — not duplicates or merge targets. Paired with `L-077`
  (filed alongside this entry, same underlying incident) as the
  diagnosis half of one finding — see `L-077`'s own curation note for why
  these are kept as two entries rather than one. Checked whether this
  belongs in `context-gaps/` or `context-observations/` instead: no to
  both — this is not a relationship CodeCompass's own graph is missing,
  nor an experience with an existing graph edge; it is a research-
  methodology gap in how this project's own primary-research role (and
  the `codecompass-template` deliverable modeling the same role for
  downstream adopters) tests a negative/invariant claim, so it correctly
  stays in `planning/learnings/`.

  **Outcome: promote (recommendation + draft for the in-repo portion;
  does not land here — the recommended destination,
  `.claude/agents/context-researcher.md`, is outside this agent's write
  boundary; the `codecompass-template` portion is outside this
  repository entirely and is flagged to the lead as a manual follow-up,
  not drafted here).** Real, specific, and already evidenced twice within
  one lineage — worth a standing rule on this occurrence rather than
  waiting for a third, matching this inbox's established practice for a
  cheap, concrete, already-evidenced fix (`L-018`/`L-023`/`L-068`'s own
  reasoning).

  **Recommended fix — add to `.claude/agents/context-researcher.md` step 2
  ("If executable behaviour exists... start there"), as a new sentence**
  (draft, for the lead to review and land; not applied here):

  > **When the behaviour under test is a negative or invariant claim
  > (e.g. "X is never reused," "Y always holds"), test the specific
  > scenario most likely to falsify it, not just one representative
  > example.** A single passing example that happens to avoid the
  > falsifying case is indistinguishable, from its own output alone, from
  > a genuinely general guarantee. Observed at Phase 79's sixth amendment:
  > an exercise's own single test deleted a non-maximum-id task and
  > concluded a deleted task's id is "never reused" generally; the real,
  > narrower guarantee (safe only if the deleted task was not, at the
  > moment of deletion, the maximum-id task) was found only once a
  > research dispatch was explicitly instructed to try multiple,
  > meaningfully different scenarios (see `L-077` for that confirmation).
  > (Phase 79 sixth amendment — L-076.)

  **Also flagged for the lead (not drafted, outside this repository):**
  the same gap most likely exists in whichever of the nine
  `codecompass-template` files models this project's own research-dispatch
  step for a downstream adopter — that template's own lightweight default
  path is the artifact the retro's bullet 2 actually describes as lacking
  "an equivalent step... built into its own lightweight default path."
  This curator cannot inspect or edit `codecompass-template` (a separate
  repository, not present in this working tree) — the lead should check
  it directly and apply the same scenario-diversity instruction there if
  confirmed missing.

  Revisit/withdraw if a future phase shows this instruction added to
  `context-researcher.md` producing disproportionate dispatch cost for
  claims where one representative example is genuinely sufficient (e.g. a
  claim with no plausible falsifying scenario distinct from the one
  tested) — not expected given how cheap the actual fix was here, but
  named as the honest revisit condition.

### L-075 — a fail-closed check's own completeness fix can correctly widen *scope* (what it looks at) while leaving *depth* (how carefully it checks what it finds) still shallow — these are separable failure axes, and closing one does not imply the other is closed

- **origin:** Phase 79 (clean-room conceptual understanding + documentation
  reconstruction), sixth amendment / `decisions/0068` item 1; retro
  Addendum 2, bullet 1; filed at this triage's own initiative per the
  addendum's explicit candidate-learning naming, deferring the
  promote/retain/discard decision to `knowledge-curator` per usual
  practice.
- **date:** 2026-10-01
- **project_revision:** `94f1e51`
- **observation:** the fifth amendment's own `check_snapshot_completeness`
  (the fix behind `L-070`) correctly widened the checker's *scope* —
  validating a snapshot's own assertion-inventory completeness, not just
  hash integrity. Its Evidence/Derivation *closure* check, however, still
  only asked "is this key present in the dict," never "does this key's
  own value actually, validly identify the record it claims to." Two real
  attack shapes were independently reproduced before the sixth amendment's
  own fix: (1) a nested table replaced by a scalar string — the key
  survives, the existing entry-iteration helper silently skips the
  malformed value, and the old closure check still counted the key as
  "captured"; (2) an identity swap — a key kept, its own `path`/
  `content_hash` re-pointed at a *different* real record with that
  record's own genuinely correct hash, invisible to pure hash-integrity
  checking since the hash is exactly right for what it actually points
  to. Fixed via a new `_validate_nested_entries` helper (returns only the
  subset of keys that are genuinely, validly captured — well-formed
  table, matching `id`, matching `kind`) and a new
  `knowledge-base-snapshot-kind-mismatch` finding, with 6 new
  `TestNestedEntryValidation` tests. This is the *third* fail-open gap
  found in the same checker's own validation logic within three
  consecutive revisions of the same ADR lineage (fourth revision's
  list-validation fix; fifth revision's snapshot-completeness fix,
  `L-070`; sixth revision's closure-value-validity fix, this entry) — and
  the general lesson this specific instance newly makes explicit is that
  "scope" and "depth" are separable failure axes: `L-070`'s own already-
  landed `CLAUDE.md` §1 sentence requires testing a mechanism's
  *minimal-content edge case*, which is a scope-shaped requirement (does
  the check look at small/empty input at all) — it does not, on its own
  wording, require testing that a key's own *value* is valid once found,
  which is what this third instance actually needed and is a depth-shaped
  requirement. A future phase following `L-070`'s landed rule to the
  letter would still not have been required to write the test that caught
  this specific bug.
- **evidence:** `decisions/0068` item 1 (full technical account of both
  attack shapes and the fix); `planning/phase-79-clean-room-understanding-and-documentation-reconstruction.md`
  §0 "Sixth revision" entry 1; `planning/retros/phase-79-clean-room-understanding-and-documentation-reconstruction.md`
  "Addendum 2: sixth amendment," bullet 1 (independently re-read directly
  — matches the ADR/plan account exactly, including the explicit
  scope-vs-depth generalization); `scripts/check_knowledge_base.py`
  (`_validate_nested_entries`, the `knowledge-base-snapshot-kind-mismatch`
  finding) / `tests/test_check_knowledge_base.py::TestNestedEntryValidation`
  (confirmed present in the actual landed code and tests, not just
  narrative); `CLAUDE.md` §1 (confirmed by direct read: the already-landed
  `L-070` sentence's exact wording — "an empty, truncated, or otherwise
  maximally-reduced input" — does not mention value-validity-of-a-present-key
  at all, confirming the gap this entry identifies in that sentence's own
  coverage).
- **classification:** project-rule
- **status:** promoted
- **recurrence:** third occurrence within this same checker/ADR lineage of
  "a fail-closed redesign still missed an edge the originally-named
  scenario didn't cover" (see `L-070`'s own recurrence note for the first
  two instances) — now a three-instance recurrence in one lineage, and
  the first instance to identify the *scope-vs-depth* distinction
  explicitly rather than just another instance of the same already-named
  pattern.
- **promoted_to:** `CLAUDE.md` §1, new sentence appended directly after the existing `L-070` sentence; mirrored into `CONTRIBUTING.md` -- user-approved per §0 @ (this phase's own closeout commit)
- **curation (this triage, 2026-10-01, knowledge-curator):** provenance
  accepted — all required fields present. Independently re-read the
  retro addendum's bullet 1, `decisions/0068`'s item 1, and the plan's own
  §0 "Sixth revision" entry 1 directly — all three agree exactly,
  including the two specific attack shapes and the fix. I separately
  re-read `CLAUDE.md` §1's actual, currently-landed `L-070` text in full
  (not just its summary in `promoted.md`/`proposed-governance-changes.md`
  §G) specifically to check whether it already covers this third
  instance — it does not: the landed sentence's own example parenthetical
  ("an empty, truncated, or otherwise maximally-reduced input") is a
  scope/minimal-content requirement, and a nested table silently replaced
  by a scalar, or a key re-pointed at a different valid record, is neither
  empty nor truncated — it is normal-sized, well-formed-looking, and
  wrong. This is a genuine gap in `L-070`'s own landed generalization, not
  a restatement of it.

  Checked for a merge/duplicate candidate: this is the most direct
  relative of any candidate in this inbox — `L-070` itself, exactly as
  this triage's own instructions anticipated. **Decision: file as a new,
  distinct entry rather than `status: merged:L-070`, because merging
  would hide a real, additional finding under a recurrence count for a
  pattern `L-070`'s own landed text does not yet fully cover** — a bare
  merge-and-increment would make it look like `L-070`'s existing
  `CLAUDE.md` rule already handles this shape (it doesn't) and would lose
  the scope-vs-depth generalization as a citable, separate finding. The
  right relationship is "builds on and extends `L-070`," recorded as a
  separate id but explicitly recommending its destination be a *second
  sentence appended to the same already-landed `CLAUDE.md` §1 passage*,
  not a competing or duplicate rule elsewhere. Checked whether this
  belongs in `context-gaps/` or `context-observations/` instead: no to
  both — this is not a relationship CodeCompass's own graph is missing,
  nor an experience with an existing graph edge; it is a validation-check
  design-discipline gap applicable project-wide, so it correctly stays in
  `planning/learnings/`.

  **Outcome: promote (recommendation + draft; does not land here — the
  recommended destination, `CLAUDE.md` §1, requires the diff-and-approval
  step `CLAUDE.md` §0 mandates, so this entry stays `status: candidate`
  until the user explicitly approves, matching `L-070`'s own precedent in
  `proposed-governance-changes.md` §G).** The recurrence bar is met (three
  structurally similar instances in one lineage, the same bar `L-070`
  itself already cleared at two), the fix is cheap (one additional
  sentence, already evidenced as sufficient to describe the actual Phase
  79 fix), and it closes a real, now-demonstrated gap in an existing,
  already-approved `CLAUDE.md` rule rather than proposing a new one from
  scratch.

  **Recommended `CLAUDE.md` §1 addition, drafted into
  `planning/v1-redefinition/proposed-governance-changes.md` as a new §H**
  (not applied to `CLAUDE.md` directly — outside this agent's write
  boundary and requires explicit user approval per §0): append a second
  sentence directly after the existing `L-070` sentence ("...can leave a
  different one at the mechanism's own edge untested. (Phase 79 fifth
  amendment — L-070.)"):

  > The same verification step must also cover the mechanism's *depth*,
  > not only its *scope*: when a check confirms that some expected key,
  > field, or entry is present, the test must separately confirm that the
  > entry's own value is well-formed and genuinely identifies or matches
  > what it claims to — a scope fix (checking that the right things are
  > looked at) does not by itself fix a depth gap (how carefully what is
  > found is checked), and closing one does not imply the other is
  > closed. (Phase 79 sixth amendment — L-075.)

  Revisit/withdraw if a future phase shows this sentence, combined with
  `L-070`'s own, making §1 read as an exhaustive validation-design
  checklist that invites skipping a genuinely different failure shape not
  named by either sentence — not expected given both are scoped narrowly
  to the two specific, evidenced shapes found so far, but named as the
  honest revisit condition.

### L-070 — a fail-closed redesign that fixes the mechanism it was asked to fix can still leave a different fail-open gap at the mechanism's own edge

- **origin:** Phase 79 (clean-room conceptual understanding + documentation
  reconstruction), fifth amendment / `decisions/0067` item 1; retro
  addendum "Addendum: fifth amendment" bullet 1; filed at this triage's
  own initiative per the addendum's explicit candidate-learning naming,
  deferring the promote/retain/discard decision to `knowledge-curator`
  per usual practice.
- **date:** 2026-10-01
- **project_revision:** `36986d3` (the fifth-amendment plan/changelog/retro
  reconciliation commit at filing time)
- **observation:** the fourth revision's own fix to
  `scripts/check_knowledge_base.py`'s snapshot-validation checks (§5.3)
  correctly addressed hashing-against-the-live-file (a legitimate
  supersession wrongly flagged as tampering) — but the historical-
  integrity/current-divergence checks it produced only ever validated
  entries already *present* in a snapshot's own `assertions` table. A
  sidecar reduced to nothing but its own `snapshot_id` iterates zero
  entries and reports zero findings, indistinguishable from a genuinely
  complete, small snapshot — a fail-open gap in *completeness*, not
  *integrity*, at a different edge of the same mechanism the fourth
  revision had just redesigned to fail closed. Fixed by a new
  `check_snapshot_completeness` function (required-metadata/type
  validation; assertion-inventory completeness checked against the real
  historical `git ls-tree` listing at the snapshot's own freeze revision,
  never the live filesystem; record-identity checking; Evidence/
  Derivation closure checking), with 11 new disposable-git-fixture tests.
  This is the *second* fail-open gap found and fixed in this same
  checker's own validation logic within two consecutive revisions of the
  same ADR (the fourth revision's own list-validation fix, §4.2, was a
  structurally similar prior instance: a block-pattern-matching detector
  missing an indentless list shape its own pattern never matched).
- **evidence:** `decisions/0067` Decision item 1 ("`check_snapshot_completeness`...
  Closes the specific gap named: a snapshot sidecar reduced to only its
  own `snapshot_id` previously produced zero findings");
  `planning/phase-79-clean-room-understanding-and-documentation-reconstruction.md`
  §0 "Fifth revision" entry 1 (full technical account) and "Fourth
  revision" entries 1-2 (the two prior, structurally similar fail-open
  fixes in the same checker/plan section); `planning/retros/phase-79-clean-room-understanding-and-documentation-reconstruction.md`
  "Addendum: fifth amendment," bullet 1 (independently re-read directly —
  matches the ADR/plan account exactly, including the explicit
  generalization: "'add a test for the exact scenario named' doesn't
  substitute for asking 'what would a maximally-reduced malicious or
  accidental input look like, and does this still catch it'"); `scripts/check_knowledge_base.py`
  / `tests/test_check_knowledge_base.py` (the actual landed fix and its
  tests, confirming the account is not just narrative).
- **classification:** project-rule
- **status:** promoted
- **recurrence:** second occurrence within this same phase/ADR (fourth
  revision's list-validation fix, then fifth revision's snapshot-
  completeness fix — both are "a fail-closed redesign still missed an
  edge the originally-named scenario didn't cover," in the same checker
  family), satisfying this project's own recurrence bar for a
  project-wide rule even though both instances are within one phase.
- **promoted_to:** `CLAUDE.md` §1, new sentence after the existing
  `L-021` sentence — approved by the user (explicit diff approval per
  `CLAUDE.md` §0) and landed @ (this phase's own closeout commit)
- **curation (this triage, 2026-10-01, knowledge-curator):** provenance
  accepted — all required fields present. Independently re-read the
  retro addendum's bullet 1, `decisions/0067`'s Decision item 1, and both
  the plan's "Fifth revision" and "Fourth revision" §0 entries directly —
  confirmed the two-instance recurrence claim by reading the fourth
  revision's own entries 1-2, not just taking the addendum's framing on
  faith; both are real, separate, structurally similar fail-open gaps in
  the same validation mechanism found across two consecutive revisions.

  Checked for a merge/duplicate candidate: grepped this inbox for
  "fail-open", "fail closed", "maximally-reduced" — no prior candidate
  addresses validation/detection-check design completeness specifically.
  `L-021` (CLAUDE.md §1, test-through-real-call-site) is the closest
  structural relative — both are "a plan's own verification section
  needs to require testing a specific additional shape, not just the
  scenario the phase's own prose names" — but `L-021` is about *wiring*
  (does the new behavior actually get called), while this is about
  *edge-case coverage* of a fail-closed check's own minimal-input case; a
  related family, not a duplicate, and not a merge target (merging would
  blur two genuinely different failure shapes under one recurrence
  count). Checked whether this belongs in `context-gaps/` or
  `context-observations/` instead: no to both — this is not a
  relationship CodeCompass's own graph is missing, nor an experience with
  an existing graph edge; it is a plan/test-design discipline gap
  applicable project-wide, so it correctly stays in `planning/learnings/`.

  **Outcome: promote, classification `project-rule`, destination
  `CLAUDE.md` §1 — pending explicit `CLAUDE.md` §0 approval before this
  status flips to `promoted`.** Unlike the other four fifth-amendment
  candidates (all scoped-rule/workflow, landable by the lead without a
  formal gate), a project-rule destined for `CLAUDE.md` requires the
  diff-and-approval step `CLAUDE.md` §0 mandates, so this entry stays
  `status: candidate` — matching this project's own established
  precedent (`planning/v1-redefinition/proposed-governance-changes.md`
  §D/E/F each record their own `L-NNN` as flipping to `promoted` only
  once the user actually approved and the edit landed, not at the
  curator's own recommendation stage). The recurrence bar is met (two
  structurally similar instances within the same phase/ADR, see above),
  and the fix is cheap and already evidenced as sufficient (the actual
  Phase 79 fix cost one new function and 13 tests, built the moment the
  gap was actually looked for). This generalizes past this specific
  checker, matching the retro addendum's own framing exactly.

  **Recommended `CLAUDE.md` §1 addition, drafted into
  `planning/v1-redefinition/proposed-governance-changes.md` as a new §G**
  (not applied to `CLAUDE.md` directly — outside this agent's write
  boundary and requires explicit user approval per §0): see that file for
  the full proposal, context, and alternatives-considered writeup. In
  summary — append to §1, after the existing `L-021` sentence:

  > If a phase's verification step tests a fail-closed validation or
  > detection mechanism (a check meant to catch malformed, incomplete, or
  > malicious input), the plan's verification section must include a test
  > against the mechanism's own minimal-content edge case (e.g. an
  > empty, truncated, or otherwise maximally-reduced input that is still
  > technically well-formed enough to be accepted for processing) in
  > addition to the originally-named failure scenario — a test that only
  > covers the scenario the phase's own prose describes is not
  > sufficient on its own, since fixing one fail-open gap in a validation
  > mechanism can leave a different one at the mechanism's own edge
  > untested. (Phase 79 fifth amendment — L-070.)

  Revisit/withdraw if the user declines the `CLAUDE.md` change — the
  underlying observation would then most likely retain as a documented,
  evidenced pattern (e.g. folded into `planning/agent-led-workflow.md`'s
  implementation step as a non-`CLAUDE.md` reminder instead) rather than
  being discarded outright, since the two-instance recurrence is real
  regardless of which artifact ultimately owns the rule.

### L-074 — a link/reference-resolution check and a real usability exercise measure different things, and the former is cheap enough to reach for even when the latter is what was actually asked for

- **origin:** Phase 79 (clean-room conceptual understanding + documentation
  reconstruction), fifth amendment / `decisions/0067` item 4; retro
  addendum "Addendum: fifth amendment" bullet 5; filed at this triage's
  own initiative per the addendum's explicit candidate-learning naming,
  deferring the promote/retain/discard decision to `knowledge-curator`
  per usual practice.
- **date:** 2026-10-01
- **project_revision:** `36986d3` (the fifth-amendment plan/changelog/retro
  reconciliation commit at filing time)
- **observation:** the original Phase 79 closeout validated
  `codecompass-template`'s usability with a fresh-clone link-integrity
  check (every markdown path resolves). A direct review found this
  doesn't test what "usability" actually means for a template meant to
  be adopted by a real downstream project. A real exercise — a fresh,
  context-free agent given only the template clone and a small invented
  non-CodeCompass project, instructed to actually adopt and use the
  template end to end — found a genuine defect invisible to any
  link-checker: an adoption instruction's "copy its contents into an
  existing one" silently collides with two files any real project
  already has (`README.md`, overwritten with a template description
  instead of the project's own; `LICENSE`, a real per-project choice).
  Every individual link in the offending instruction still resolved
  fine — the defect is in what a literal reading does to a second,
  pre-existing file on the target side, a category of failure a
  link-checker cannot model at all. The exercise also surfaced a
  genuine, inherent tension (freezing a snapshot requires a commit; the
  exercise's own no-commit rule meant one record was honestly left
  partially frozen) that again no link-checker could find.
- **evidence:** `decisions/0067` Decision item 4 ("A real downstream
  usability exercise... replaces the original fresh-clone link-check...
  finding and fixing one genuine adoption-instruction defect"); `planning/phase-79-clean-room-understanding-and-documentation-reconstruction.md`
  §0 "Fifth revision" entry 4 (full technical account, including the
  README/LICENSE collision and the snapshot/no-commit tension);
  `planning/retros/phase-79-clean-room-understanding-and-documentation-reconstruction.md`
  "Addendum: fifth amendment," bullet 5 (independently re-read directly,
  not taken on the addendum's own summary alone — matches the ADR/plan
  account exactly).
- **classification:** workflow
- **status:** promoted
- **recurrence:** first occurrence of this specific substitution (a
  cheap structural check standing in for a real usability exercise);
  conceptually related to, but a distinct shape from, `L-021`'s already-
  landed `CLAUDE.md` §1 rule (a test that only exercises a function in
  isolation isn't sufficient when a real call site exists) — this
  generalizes that same "narrow proxy isn't a substitute for the real
  exercise" principle from a code call site to a downstream deliverable's
  usability claim.
- **promoted_to:** `planning/agent-led-workflow.md` step 7, new paragraph
  (link-check-vs-usability-exercise distinction) @ (this phase's own
  closeout commit)
- **curation (this triage, 2026-10-01, knowledge-curator):** provenance
  accepted — all required fields present. Independently re-read the
  retro addendum's bullet 5, `decisions/0067`'s Decision item 4, and the
  plan's own §0 "Fifth revision" entry 4 directly, rather than trusting
  any one summary alone — all three agree on the exact mechanism (a
  link-checker cannot model a same-filename collision on the adopting
  side) and the exact defect found.

  Checked for a merge/duplicate candidate: grepped this inbox for
  "usability", "link-check", "link-resolution" — no prior candidate
  addresses this substitution. Related in spirit to `L-021` (CLAUDE.md
  §1, narrow-scope test insufficiency) and `L-027` (single-trial
  baseline/treatment comparisons can't separate tool contribution from
  diligence variance) but distinct in shape from both — not a duplicate
  or a merge target for either. Checked whether this belongs in
  `context-gaps/` or `context-observations/` instead: no to both — this
  is not a relationship CodeCompass's own graph is missing, nor an
  experience with an existing graph edge; it is a verification-design gap
  in how this project's own workflow validates a downstream deliverable,
  so it correctly stays in `planning/learnings/`.

  **Outcome: promote (recommendation + draft; does not land here — the
  recommended destination, `planning/agent-led-workflow.md`, is outside
  this agent's write boundary).** Real, specific, structurally
  significant (the original check gave a false sense of validation — it
  passed cleanly while a real defect sat one layer below what it could
  see), and cheap to generalize into a standing habit: whenever a plan's
  verification step is meant to validate a deliverable's real-world
  usability, name the real exercise explicitly rather than accepting a
  cheaper structural proxy as sufficient. Matches the same "close it
  while the fallback is evidenced" reasoning `L-018`/`L-023`/`L-046`/
  `L-069` already used.

  **Recommended fix — add a note near step 7 of
  `planning/agent-led-workflow.md`, in the independent-evaluation
  cluster** (draft, for the lead to review and land; not applied here):

  > **A link/reference-resolution check and a real usability exercise
  > measure different things, and the former is cheap enough to reach
  > for by default even when the latter is what was actually asked
  > for.** If a plan's verification step is meant to validate that a
  > deliverable (a template, a generated artifact meant for downstream
  > human/agent use) is actually usable, name the real exercise
  > explicitly — a fresh, context-limited agent actually adopting/using
  > it against a small real or invented target — rather than treating a
  > check that every link resolves as sufficient. A link-checker cannot
  > find a defect that is only visible when the instructions are
  > followed literally against a real second target (e.g. a filename
  > collision the instructions don't anticipate), even when every
  > individual link in the offending instruction resolves fine.
  > Generalizes `CLAUDE.md` §1's `L-021` rule (a narrow-scope test isn't
  > sufficient on its own) from code call sites to deliverable-usability
  > claims. Observed at Phase 79's fifth amendment: a fresh-clone
  > link-integrity check passed cleanly on `codecompass-template`; a
  > real adoption exercise against a small invented project found a
  > genuine defect (a `README.md`/`LICENSE` collision) invisible to any
  > link-checker. (Phase 79 fifth amendment — L-074.)

  Revisit/withdraw if a future phase shows the real-exercise requirement
  adding disproportionate dispatch cost for deliverables where a
  structural check is genuinely sufficient (e.g. a deliverable with no
  "a human/agent follows these steps against their own project" shape at
  all) — not expected given how directly a template fits this shape, but
  named as the honest revisit condition.

### L-073 — this session's own local dispatch transcripts remained genuine, recoverable evidence well after each dispatch completed, worth checking before assuming a rerun is the only way to get missing evidence

- **origin:** Phase 79 (clean-room conceptual understanding + documentation
  reconstruction), fifth amendment / `decisions/0067` item 3(a); retro
  addendum "Addendum: fifth amendment" bullet 4; filed at this triage's
  own initiative per the addendum's explicit candidate-learning naming,
  deferring the promote/retain/discard decision to `knowledge-curator`
  per usual practice.
- **date:** 2026-10-01
- **project_revision:** `36986d3` (the fifth-amendment plan/changelog/retro
  reconciliation commit at filing time)
- **observation:** the original Phase 79 closeout's isolation-verdict
  evidence was thin: the persisted Tier 1 preflight record was the probe
  dispatch's own prose handback, and no per-dispatch manifest, raw
  transcript, or independent boundary check existed for any of the six
  isolation-sensitive pilot dispatches beyond that one probe. Rather than
  treating this gap as unrecoverable (requiring either an unsupported
  claim or a fresh rerun, which could not have reproduced the *original*
  execution anyway), this session's own original dispatch transcripts
  were found still present on local disk, not rerun or reconstructed. A
  real, mechanical boundary-check script was built and run against all
  six raw transcripts, recovering genuine access-log evidence that did
  not exist before — including a real boundary deviation in one dispatch
  (the coding-context packet-assembly step read two files outside its
  stated scope) that the original prose-only evidence had no way of
  catching.
- **evidence:** `decisions/0067` Decision item 3 ("newly-recovered,
  genuinely mechanical boundary-check evidence (derived from the original
  pilot dispatches' own still-extant transcripts, not a rerun)");
  `planning/phase-79-clean-room-understanding-and-documentation-reconstruction.md`
  §0 "Fifth revision" entry 3(a) (full technical account, including the
  specific boundary deviation found); `planning/retros/phase-79-clean-room-understanding-and-documentation-reconstruction.md`
  "Addendum: fifth amendment," bullet 4 (independently re-read directly —
  matches the ADR/plan account exactly).
- **classification:** workflow
- **status:** promoted
- **recurrence:** first occurrence of this specific recovery technique
  being used (and recorded) in this project.
- **promoted_to:** `planning/agent-led-workflow.md` step 7, new paragraph
  (check local transcript/session state before assuming evidence is
  unrecoverable) @ (this phase's own closeout commit)
- **curation (this triage, 2026-10-01, knowledge-curator):** provenance
  accepted — all required fields present. Independently re-read the
  retro addendum's bullet 4, `decisions/0067`'s Decision item 3, and the
  plan's own §0 "Fifth revision" entry 3(a) directly — all three agree on
  the mechanism (original transcripts read directly, not a rerun) and the
  specific real finding recovered (the packet-assembly boundary
  deviation).

  Checked for a merge/duplicate candidate: grepped this inbox for
  "transcript" and "session state" — the only prior transcript-related
  entries (the `L-046` cluster, token-exposure-in-transcript) address a
  different concern entirely (a secret typed into the visible
  conversation transcript), not evidence recoverable from a *dispatched
  subagent's own* transcript after the fact — not a duplicate or merge
  target. Checked whether this belongs in `context-gaps/` or
  `context-observations/` instead: no to both — this is not a
  relationship CodeCompass's own graph is missing, nor an experience with
  an existing graph edge; it is a workflow-level evidence-gathering habit
  for this project's own agent-led development process, so it correctly
  stays in `planning/learnings/`.

  **Outcome: promote (recommendation + draft; does not land here — the
  recommended destination, `planning/agent-led-workflow.md`, is outside
  this agent's write boundary).** Real, specific, and genuinely useful:
  it changed what was actually possible at Phase 79 (recovering real
  evidence instead of either leaving a gap unaddressed or fabricating
  equivalence with a rerun), so it earns a standing reminder on first
  occurrence rather than waiting for recurrence, matching
  `L-018`/`L-023`/`L-046`/`L-069`/`L-074`'s own reasoning. Noted
  explicitly as a *check this before assuming otherwise* habit, not a
  guarantee — the entry itself flags the recoverability window is not
  indefinite.

  **Recommended fix — add a note near step 7 of
  `planning/agent-led-workflow.md`, in the independent-evaluation
  cluster** (draft, for the lead to review and land; not applied here):

  > **Before concluding a piece of boundary/compliance evidence is
  > unrecoverable and that a dispatch must be rerun to produce it, check
  > whether the original dispatch's own transcript/session state is
  > still present on local disk.** This session's own prior dispatch
  > transcripts remained available well after each dispatch completed,
  > and a mechanical pass over them produced genuine, previously-missing
  > evidence (including a real finding no prior prose self-report had
  > caught) without needing to fabricate anything or treat a fresh rerun
  > as equivalent to the original execution (a rerun cannot reproduce the
  > *original* execution's own state regardless). Observed at Phase 79's
  > fifth amendment: the original isolation-verdict evidence was one
  > dispatch's own prose handback; reading the six pilot dispatches' own
  > still-extant raw transcripts directly recovered real, previously
  > unavailable boundary-check evidence, including a genuine deviation.
  > Check for this before assuming a rerun — or an unsupported claim — is
  > the only option; the recoverability window is not known to be
  > indefinite, so check promptly rather than assuming it will still be
  > there much later. (Phase 79 fifth amendment — L-073.)

  Revisit/withdraw if a future phase shows local transcripts are
  reliably *not* recoverable after some specific, now-known window
  (narrowing the note's usefulness to "check immediately, never later")
  — not yet known from a single occurrence, so left as an open question
  rather than asserted as a guarantee.

### L-072 — "honestly labelled" and "achieved" are different claims and must never share one verdict token, even when both happen to be favorable

- **origin:** Phase 79 (clean-room conceptual understanding + documentation
  reconstruction), fifth amendment / `decisions/0067` item 3(b); retro
  addendum "Addendum: fifth amendment" bullet 3; filed at this triage's
  own initiative per the addendum's explicit candidate-learning naming,
  deferring the promote/retain/discard decision to `knowledge-curator`
  per usual practice.
- **date:** 2026-10-01
- **project_revision:** `36986d3` (the fifth-amendment plan/changelog/retro
  reconciliation commit at filing time)
- **observation:** both the original Phase 79 closeout audit report and
  its re-audit stated "Track 2 (strict clean-room isolation validation):
  PASS." Every piece of evidence behind that line was itself accurate —
  the `best-effort` self-labelling by the isolation-sensitive dispatches
  really had been checked and really did hold, and the plan's own §6.5
  rule ("Tier 2 is always best-effort") was never violated in substance.
  The defect was purely in how that accurate finding got summarized: the
  phrase reads as isolation having actually succeeded, when what had been
  verified was only that the dispatches' own honest labelling of
  themselves as best-effort was accurate. Corrected to "Track 2: UNMET,"
  reported separately from, and unaffected by, Track 1's own real PASS.
- **evidence:** `decisions/0067` Decision item 3 ("The closeout's own
  'Track 2... PASS' language... is corrected to Track 2: UNMET");
  `planning/phase-79-clean-room-understanding-and-documentation-reconstruction.md`
  §0 "Fifth revision" entry 3 ("a reporting defect, not a design defect —
  the plan's own §6.5 rule... was never violated in substance") and its
  own Status line ("its own 'Track 2 PASS' language is corrected by the
  fifth revision... to Track 2: UNMET, reported separately and
  unaffected by Track 1"); `planning/retros/phase-79-clean-room-understanding-and-documentation-reconstruction.md`
  "Addendum: fifth amendment," bullet 3 (independently re-read directly —
  matches the ADR/plan account exactly).
- **classification:** scoped-rule
- **status:** promoted
- **recurrence:** first occurrence of this specific conflation (a
  single verdict token standing in for two distinct claims); distinct
  from `L-001`'s conflation (highest-done-phase vs. product-completeness,
  a different pair of claims) but the same general failure family
  (one summary word carrying more than one meaning).
- **promoted_to:** `.claude/agents/release-phase-auditor.md` "Hard rules"
  (verdict-token rule) @ (this phase's own closeout commit)
- **curation (this triage, 2026-10-01, knowledge-curator):** provenance
  accepted — all required fields present. Independently re-read the
  retro addendum's bullet 3, `decisions/0067`'s Decision item 3, and the
  plan's own §0 "Fifth revision" entry 3 and Status line directly — all
  agree exactly, including the explicit "reporting defect, not a design
  defect" framing.

  Checked for a merge/duplicate candidate: grepped this inbox for
  "verdict", "PASS", "conflat" — `L-001` (conflates "highest done phase"
  with "product completeness," a `check_readme_phase_count` defect) and
  `L-043` (no mechanical check cross-references a learning candidate's
  own status against its curation-note verdict) are related in *theme*
  (summary tokens hiding more than they say) but address different
  artifacts and different pairs of claims — not duplicates or merge
  targets. Checked whether this belongs in `context-gaps/` or
  `context-observations/` instead: no to both — this is not a
  relationship CodeCompass's own graph is missing, nor an experience with
  an existing graph edge; it is a reporting-discipline gap in how this
  project's own closeout/audit process communicates verdicts, so it
  correctly stays in `planning/learnings/`.

  **Outcome: promote (recommendation + draft; does not land here — the
  recommended destination, `.claude/agents/release-phase-auditor.md`, is
  outside this agent's write boundary).** Real, specific, and about
  exactly the artifact (a verdict line) a reader relies on most and reads
  most superficially — worth a standing rule on first occurrence rather
  than waiting for recurrence, matching this inbox's own established
  practice for a cheap, concrete, already-evidenced fix.

  **Recommended fix — add to `.claude/agents/release-phase-auditor.md`
  "Hard rules"** (draft, for the lead to review and land; not applied
  here):

  > **Never let one verdict token answer two different questions.** If a
  > report must state both whether something was *honestly labelled*
  > (e.g. a best-effort boundary accurately disclosed as best-effort)
  > and whether it was *actually achieved* (e.g. strict isolation
  > genuinely enforced), give each its own verdict line — never a single
  > shared `PASS`/`FAIL` covering both, even when both happen to be
  > favorable. A reader of a shared token cannot tell which claim it
  > refers to. When auditing a phase whose own design draws this
  > distinction (e.g. a multi-track verification scheme with an
  > honesty-as-the-control track), check the phase's own report for this
  > conflation specifically, and do not reproduce it in this agent's own
  > audit verdict either. Observed at Phase 79's fifth amendment: a
  > closeout report's "Track 2 (strict clean-room isolation validation):
  > PASS" was accurate about honest labelling but was read as isolation
  > having succeeded; corrected to "Track 2: UNMET," reported separately
  > from Track 1's own real PASS. (Phase 79 fifth amendment — L-072.)

  Revisit/withdraw if a future phase shows this rule producing verdict
  reports that are harder to act on (e.g. too many separately-tracked
  tokens for a reader to follow) — not expected given the rule only
  applies when a phase's own design already draws the distinction, not
  to every verdict generally.

### L-071 — a merge/reconciliation step that preserves prior facts can still silently drop prior structure, and no later verification pass is guaranteed to check for that structure's survival specifically

- **origin:** Phase 79 (clean-room conceptual understanding + documentation
  reconstruction), fifth amendment / `decisions/0067` item 2; retro
  addendum "Addendum: fifth amendment" bullet 2; filed at this triage's
  own initiative per the addendum's explicit candidate-learning naming,
  deferring the promote/retain/discard decision to `knowledge-curator`
  per usual practice.
- **date:** 2026-10-01
- **project_revision:** `36986d3` (the fifth-amendment plan/changelog/retro
  reconciliation commit at filing time)
- **observation:** the clean-room draft's own inline
  `first-party-source-symbols@v2#CL-FPSS-NNN` citations existed, were
  correct, and were lost specifically at the one step —
  `docs-maintainer`'s legacy-reconciliation merge of the draft's content
  into the existing `architecture/overview.md`/`architecture/context-graph-schema.md`
  pages — that was never itself re-checked for having preserved them.
  The merge preserved the prose but dropped every citation. Two
  independent verification passes that *did* run afterward (documentation
  Q&A, coding-context evaluation) both happened to check factual
  accuracy, not citation presence, so neither caught the loss. Fixed by
  restoring a citation (with a navigable relative link to the real
  backing Claim record) at every point in both pages tracing to a
  specific assertion, each verified to resolve to a real file and an
  actual snapshot-v2 member.
- **evidence:** `decisions/0067` Decision item 2 ("`architecture/overview.md`/
  `architecture/context-graph-schema.md` regain their... citations, lost
  during the legacy-reconciliation merge"); `planning/phase-79-clean-room-understanding-and-documentation-reconstruction.md`
  §0 "Fifth revision" entry 2 (full technical account, including which
  pass was responsible and what the two later verification passes
  checked instead); `planning/retros/phase-79-clean-room-understanding-and-documentation-reconstruction.md`
  "Addendum: fifth amendment," bullet 2 (independently re-read directly —
  matches the ADR/plan account exactly).
- **classification:** scoped-rule
- **status:** promoted
- **recurrence:** first occurrence of this specific failure shape (a
  merge step dropping structural elements, e.g. citations, while
  preserving factual prose); related in *family* to `L-068` (also a
  Phase-79 legacy-reconciliation-mode gap) but a distinct failure stage —
  `L-068` is about the evidentiary bar a `supported` classification
  requires once a passage has already been compared; this is about
  verifying the merge *output itself* retained a structural element the
  input had, a check that happens (or doesn't) after the classification
  step `L-068` covers.
- **promoted_to:** `.claude/agents/docs-maintainer.md` "Legacy
  reconciliation mode" (post-merge citation-survival check) @ (this
  phase's own closeout commit)
- **curation (this triage, 2026-10-01, knowledge-curator):** provenance
  accepted — all required fields present. Independently re-read the
  retro addendum's bullet 2, `decisions/0067`'s Decision item 2, and the
  plan's own §0 "Fifth revision" entry 2 directly — all agree exactly,
  including which two verification passes ran and what each one actually
  checked.

  Checked for a merge/duplicate candidate: grepped this inbox for
  "citation" broadly — the `L-048`/`L-051`/`L-055` citation-fragility
  cluster is a *different* failure mode (a citation going stale because
  the thing it points at moved or was restructured, not a citation being
  dropped entirely during a content merge) and a different artifact class
  (domain-corpus illustrative citations of planning documents, not
  architecture-doc citations of frozen knowledge-base Claims) — not a
  duplicate or merge target, though related in the general sense that
  this project's own citation mechanisms keep surfacing new failure
  shapes. Also not a duplicate of `L-068` (see recurrence note above).
  Checked whether this belongs in `context-gaps/` or
  `context-observations/` instead: no to both — this is not a
  relationship CodeCompass's own graph is missing, nor an experience with
  an existing graph edge; it is a process gap in how this project's own
  `docs-maintainer` "Legacy reconciliation mode" verifies its own merge
  output, so it correctly stays in `planning/learnings/`.

  **Outcome: promote (recommendation + draft; does not land here — the
  recommended destination, `.claude/agents/docs-maintainer.md`, is
  outside this agent's write boundary).** Real, specific, and
  structurally significant in the same way `L-068` was: it survived two
  independent verification passes because neither was looking for this
  particular kind of loss — exactly the shape that justifies closing a
  real, disclosed gap on first occurrence (`L-018`/`L-023`/`L-068`'s own
  reasoning) with a concrete, cheap fallback (a direct pre/post citation
  diff) rather than waiting for recurrence. The general habit — when a
  merge/reconciliation step is expected to preserve prior *structure*,
  not only prior *facts*, check for that structure's survival explicitly
  — generalizes past citations specifically, but the recommended fix
  below is scoped to the one concrete instance this phase evidenced.

  **Recommended fix — add to `.claude/agents/docs-maintainer.md`
  "Legacy reconciliation mode," after the existing "Re-grounding, not
  default restoration" paragraph** (draft, for the lead to review and
  land; not applied here):

  > **Verify structure survived the merge, not only that the resulting
  > prose is still accurate.** When merging a clean-room draft's content
  > into existing narrative documentation, any inline citation (or other
  > structural element the draft deliberately carried — a cross-
  > reference, a navigable link) must still be present in the merged
  > output. Before considering a legacy-reconciliation merge complete,
  > diff the draft's own citation list against the merged page directly
  > — the published narrative reading as factually accurate is not
  > evidence its citations survived, since a prose-preserving merge can
  > silently drop them. Observed at Phase 79 (fifth amendment, `L-071`):
  > the clean-room draft's own `first-party-source-symbols@v2#CL-FPSS-NNN`
  > citations were present pre-merge and entirely absent post-merge, and
  > two later independent verification passes (documentation Q&A,
  > coding-context evaluation) both checked factual accuracy and neither
  > checked citation presence, so the loss went undetected until a direct
  > review.

  Also worth the lead's consideration (not drafted in full here, to keep
  this recommendation narrowly scoped to the one agent whose own output
  this is): whether `release-phase-auditor`'s docs-drift-audit DoD check
  (`CLAUDE.md` §5, "What to check" item 3) should gain a cross-check that
  a legacy-reconciliation merge's citation count didn't drop, as a
  second line of defense independent of `docs-maintainer`'s own
  self-check above — left as an open question since `L-071` alone only
  evidences the self-check's absence, not a case where a second
  independent layer would have mattered differently.

  Revisit/withdraw if a future legacy-reconciliation merge shows this
  check adding overhead disproportionate to the defects it catches (e.g.
  if dropped citations turn out to be rare once the merge step is done
  more carefully in general) — not expected given how cheap the actual
  catch would have been here (a direct citation-count diff), but named as
  the honest revisit condition.

### L-069 — a hand-built curated code export (manual `sed` line-range extraction) produced two real truncation bugs that reached an isolated dispatch and caused a wasted pass and a false "internal inconsistency" finding

- **origin:** Phase 79 (clean-room conceptual understanding +
  documentation reconstruction, `decisions/0066`), retro "What didn't
  work" (first bullet); filed at this triage's own initiative per the
  retro's own explicit candidate-learning proposal, deferring the
  promote/retain/discard decision to `knowledge-curator` per usual
  practice.
- **date:** 2026-10-01
- **project_revision:** `a1144f9` (Phase 79's latest closeout-adjacent
  commit at filing time; `planning/retros/phase-79-clean-room-understanding-and-documentation-reconstruction.md`
  itself uncommitted at filing time, per this session's own git status)
- **observation:** the Implementation-reconstruction export for the
  first-party-source-symbols pilot topic (`src/codecompass/source_symbols.py`
  plus `graph_schema_fragment.py`) was hand-curated via manual `sed`
  line-range extraction. Two separate truncation bugs made it into the
  version handed to the *first* `implementation-reconstructor` dispatch:
  a dataclass cut off mid-definition, and a dangling function signature.
  That dispatch's own report surfaced an apparent internal inconsistency
  — `SourceSymbolRow` reported as missing `line`/`purpose`/`exposure`
  fields that `_sync_source_symbols` reads off it — which traced back to
  the truncated export, not a real code defect. It was caught (per the
  retro's own "What worked" bullet on reading dispatch reports carefully
  rather than rubber-stamping them) before being trusted, the export was
  corrected, and a second dispatch confirmed the inconsistency was an
  artifact of the truncation, not a real finding — but the first dispatch
  was fully wasted and a false finding was live, disclosed, and had to be
  walked back before the re-run.
- **evidence:** `planning/retros/phase-79-clean-room-understanding-and-documentation-reconstruction.md`
  "What didn't work" bullet 1 ("Building the curated schema-extract
  export by hand with `sed` line ranges was error-prone..."); independently
  cross-checked against `planning/knowledge/first-party-source-symbols/implementation-reconstruction.md`
  lines 15-20 ("Note on this revision: this export was corrected since a
  prior reconstruction pass. That pass reported `SourceSymbolRow` as
  missing `line`/`purpose`/`exposure` fields... an apparent internal
  inconsistency. Re-reading the export fresh: this is no longer
  present.") and lines 156-165 ("Verification of the previously-reported
  inconsistency (now resolved)") — both independently confirm the retro's
  account, not just restate it.
- **classification:** workflow
- **status:** promoted
- **recurrence:** first occurrence
- **promoted_to:** `planning/agent-led-workflow.md` step 5, new paragraph
  ("A hand-curated code export built via manual `sed`/line-range
  extraction should be self-validated before being handed to an isolated
  dispatch...") @ (this phase's own closeout commit)
- **curation (Phase 79 triage, 2026-10-01, knowledge-curator):**
  provenance accepted — all required fields present. Independently
  re-read the retro's "What didn't work" bullet 1 directly, then verified
  it against the actual knowledge-base artifact it describes
  (`implementation-reconstruction.md`'s own two self-disclosing sections)
  rather than trusting the retro's summary alone — both match exactly,
  including the two specific truncation shapes (mid-definition dataclass,
  dangling signature) and the false-finding mechanism.

  Checked for a merge/duplicate candidate: grepped this inbox for
  "sed"/"truncat"/"curated export" — no prior candidate addresses
  hand-built export construction quality; not a duplicate of `L-019`
  (a *different* export-construction failure mode: a hand-written
  placeholder fixture causing one-time content-hash "false churn," not a
  structural truncation bug) or `L-062` (restricts *reads*, not export
  *construction correctness*). Checked whether this belongs in
  `context-gaps/` or `context-observations/` instead: no to both — this
  is not a relationship CodeCompass's own graph is missing, nor an
  experience with an existing graph edge; it is a dispatch-preparation
  discipline gap in this project's own agent-led workflow, so it
  correctly stays in `planning/learnings/`.

  **Outcome: promote (recommendation + draft; does not land here — the
  recommended destination, `planning/agent-led-workflow.md`, is outside
  this agent's write boundary).** Real, specific, single-occurrence, but
  cheap to fix and cheap to verify (a parse check costs near nothing next
  to a full wasted dispatch), matching the same "close it while the
  fallback is evidenced" reasoning `L-018`/`L-023`/`L-046` already used
  rather than waiting for a second phase to independently rediscover the
  same failure mode. Scoped narrowly to *hand-built* exports constructed
  via manual line-range extraction specifically — not a general claim
  that every export needs validation (a mechanically-generated export,
  e.g. one produced by a script, doesn't have this specific failure
  mode).

  **Recommended fix — add a note near step 5 of
  `planning/agent-led-workflow.md`, alongside the existing `L-018`/`L-023`/
  `L-062` dispatch-preparation cluster** (draft, for the lead to review
  and land; not applied here):

  > **Before handing a hand-curated code export (e.g. built via manual
  > `sed` line-range extraction) to an isolated dispatch, self-validate
  > that the extracted fragment is actually well-formed** — for Python,
  > confirm it parses (e.g. `ast.parse` against the fragment) before
  > treating it as dispatch-ready; for another language, the closest
  > equivalent. Observed at Phase 79: a hand-built export had two separate
  > `sed` line-range truncation bugs (a dataclass cut off mid-definition,
  > a dangling function signature) that reached the first
  > `implementation-reconstructor` dispatch and produced a false "internal
  > inconsistency" finding, wasting a full dispatch pass before being
  > caught and corrected on a re-run. A parse check before dispatch would
  > have caught both for near-zero cost. (Phase 79 — L-069.)

  Revisit/withdraw if a future isolation-sensitive phase builds its
  curated export via a small script rather than hand-editing line ranges
  (removing the failure mode structurally, per the retro's own
  suggestion) and the user judges the process-doc note no longer earns
  its keep.

### L-068 — a legacy-reconciliation `supported` classification based on cross-document agreement is not the same as the claim being checked against primary evidence, and both can independently echo the same wording error

- **origin:** Phase 79 (clean-room conceptual understanding +
  documentation reconstruction, `decisions/0066`), retro "What worked"
  (last bullet) + "Anything worth remembering" (first bullet); filed at
  this triage's own initiative per the retro's own explicit candidate-
  learning proposal, deferring the promote/retain/discard decision to
  `knowledge-curator` per usual practice.
- **date:** 2026-10-01
- **project_revision:** `a1144f9` ("fix(phase-79): correct core.Ecosystem
  cardinality in architecture/overview.md" — the fix commit itself;
  `planning/retros/phase-79-clean-room-understanding-and-documentation-reconstruction.md`
  uncommitted at filing time, per this session's own git status)
- **observation:** `planning/knowledge/first-party-source-symbols/legacy-reconciliation.md`
  classified the legacy claim "`core.Ecosystem` can't distinguish JS/TS;
  `source_symbols.Language` exists for that reason" as `supported`, with
  disposition "Unchanged — matches CL-FPSS-001 exactly." Both the legacy
  prose (`architecture/overview.md:845` at the time) and `CL-FPSS-001`
  stated `core.Ecosystem` "has one value (`NPM`)" — actually wrong:
  `src/codecompass/core.py`'s `Ecosystem` enum has **four** values
  (`NPM`, `PYTHON`, `CARGO`, `HASKELL`); only the `NPM` value collapses
  JS/TS. The wrong cardinality traces to `decisions/0065`'s own
  already-Accepted prose ("`core.Ecosystem` has exactly one value
  (`NPM`) covering both JavaScript and TypeScript dependencies
  identically"), echoed near-verbatim into `architecture/overview.md`,
  and echoed again into `CL-FPSS-001` during this same phase's own
  clean-room research — three documents in full agreement, all wrong the
  same way, because none had been checked against `core.py` directly.
  The legacy-reconciliation classification pass matched the clean-room
  draft's wording against the legacy doc's wording and treated that
  agreement as sufficient for `supported`, without an independent
  primary-evidence check of the one specific, checkable fact involved
  (the enum's cardinality). The error was caught only by a later,
  separate documentation-only Q&A verification pass that read `core.py`
  directly and flagged the claim **WRONG**; the doc fix landed in commit
  `a1144f9`.
- **evidence:** `planning/knowledge/first-party-source-symbols/legacy-reconciliation.md:40`
  (the `supported` classification row and its "matches CL-FPSS-001
  exactly" disposition); `decisions/0065-first-party-source-is-language-classified-occurrence-identified-and-honestly-graded.md:37-39`
  (the original "`core.Ecosystem` has exactly one value (`NPM`)" prose,
  the root of the error); `planning/knowledge/first-party-source-symbols/implementation-reconstruction.md:46-79`
  ("1. `Language` vs `core.Ecosystem` — **WRONG**" — the independent
  verification against `src/codecompass/core.py:13-19`'s real four-value
  enum) and `:189-208` (summary table + recommended fix); `architecture/overview.md:845`
  (current, fixed text: "`core.Ecosystem` is a 4-value enum..."), fixed at
  commit `a1144f9`; `planning/retros/phase-79-clean-room-understanding-and-documentation-reconstruction.md`
  "What worked" last bullet + "Anything worth remembering" first bullet —
  both independently re-read directly, not taken on the task's own
  summary alone, and both match this entry's account exactly.
- **classification:** scoped-rule
- **status:** promoted
- **recurrence:** first occurrence of this specific failure shape (a
  `supported` classification granted on cross-document/draft agreement
  alone, with no primary-evidence spot-check of a concrete, checkable
  fact embedded in the claim) — distinct in kind from `L-033`'s
  within-page-consistency gap and `L-058`'s whole-repository-grep gap,
  both of which are about search *completeness*, not about what evidence
  bar a `supported` classification itself requires.
- **promoted_to:** `.claude/agents/docs-maintainer.md` "Legacy
  reconciliation mode," extending the `supported` bullet @ (this phase's
  own closeout commit)
- **curation (Phase 79 triage, 2026-10-01, knowledge-curator):**
  provenance accepted — all required fields present. Independently
  re-read the retro's two cited sections directly, then traced the claim
  through all four artifacts it touches (`decisions/0065`,
  `architecture/overview.md`, `legacy-reconciliation.md`,
  `implementation-reconstruction.md`) rather than trusting the retro's
  characterization alone — every link in the chain checks out exactly as
  the retro describes, including the specific line numbers and the exact
  wording each document independently echoed.

  Checked for a merge/duplicate candidate: grepped this inbox for
  "legacy reconcil"/"cross-document"/"primary evidence"/"Ecosystem" — no
  prior candidate addresses the legacy-reconciliation `supported` bar
  specifically. Not a duplicate of `L-033` (within-*page* self-
  contradiction, a `domain-skeptic` step) or `L-058` (whole-*repository*
  grep completeness, a `docs-maintainer` current-truth-reconciliation
  step) — both of those are about search breadth; this is about the
  evidentiary bar a specific classification value (`supported`) requires
  once a candidate passage has already been found and compared, a
  distinct failure stage. Checked whether this belongs in `context-gaps/`
  or `context-observations/` instead: no to both — this is not a
  relationship CodeCompass's own graph is missing, nor an experience with
  an existing graph edge; it is a process gap in how this project's own
  Phase-79 legacy-reconciliation mode (`.claude/agents/docs-maintainer.md`
  "Legacy reconciliation mode") defines its own `supported` bar, so it
  correctly stays in `planning/learnings/`. Also note: `decisions/0065`
  itself is out of scope for a fix — per `CLAUDE.md` §0/§2, ADRs are
  append-only and this isn't a reversed decision, only an easily-misread
  sentence in an already-Accepted ADR; the actual, already-landed fix
  (commit `a1144f9`) correctly targeted the living `architecture/`
  doc, not the ADR.

  **Outcome: promote (recommendation + draft; does not land here — the
  recommended destination, `.claude/agents/docs-maintainer.md`, is
  outside this agent's write boundary, and this task did not grant a
  narrow direct-edit exception the way Phase 54c's triage did for
  `L-024`).** Real, specific, single-occurrence, but structurally
  significant: this failure mode survived an ADR, a phase plan, and this
  phase's own dedicated legacy-reconciliation pass, three independent-
  looking checks that all shared the same blind spot (agreement between
  documents, never a primary-source check) — exactly the shape
  `L-018`/`L-023` used to justify closing a real, disclosed gap on first
  occurrence rather than waiting for recurrence, since the fallback
  (a targeted primary-evidence spot-check) is already concrete, cheap,
  and evidenced as sufficient (the actual catch here took one read of
  `core.py`).

  **Recommended fix — extend the `supported` bullet in
  `.claude/agents/docs-maintainer.md`'s "Legacy reconciliation mode"
  section** (draft, for the lead to review and land; not applied here):

  > **A `supported` classification needs at least one primary-evidence
  > check, not only cross-document agreement.** If the legacy claim
  > states a concrete, checkable fact (a cardinality, a count, an
  > enumerated value set, a specific number or threshold), verify that
  > specific fact directly against the real source (the actual code,
  > schema, or config) before classifying it `supported` — matching the
  > clean-room draft's own wording, or another architecture page's
  > wording, is not sufficient by itself, because multiple documents can
  > independently echo the same original wording error and all agree
  > while all being wrong. Observed at Phase 79: `core.Ecosystem`'s
  > cardinality was classified `supported` because it matched
  > `CL-FPSS-001` exactly — both had silently inherited a wrong "has
  > exactly one value" claim from `decisions/0065`'s own prose, uncaught
  > until a separate documentation-only Q&A pass read `core.py` directly.
  > (Phase 79 — L-068.)

  Revisit/withdraw if a future legacy-reconciliation pass shows this
  primary-evidence check adding overhead disproportionate to the defects
  it catches (e.g. if most legacy claims are non-quantitative/non-
  checkable and the check rarely applies) — not expected given how cheap
  the actual catch was here, but named as the honest revisit condition
  rather than treating this as permanent on one occurrence alone.

### L-067 — two related schema/plan-design heuristics surfaced during Phase 77's second amendment (binary-first-guess is often wrong for a cross-language concept; live-verify a natural key against ordinary, non-edge-case real code before committing to schema) — real and evidenced, but single-phase, not yet promotable to one specific artifact

- **origin:** Phase 77 (First-party source awareness + `codecompass-template`)
  retro "Lessons learnt" (both bullets) — filed at this triage's own
  initiative after independently assessing the retro's "Candidate
  learnings filed" section, which stated "none new this phase," per
  `CLAUDE.md` §8's reservation of that judgment call to `knowledge-curator`
  triage, not the retro-writing lead's own say-so (matching `L-029`'s own
  precedent for exactly this situation).
- **date:** 2026-09-29
- **project_revision:** `fa47972` (Phase 77's second plan amendment,
  where both corrections actually landed as text, before implementation)
- **observation:** two distinct schema/ontology corrections in the same
  amendment round shared a common shape: (1) `source_symbols.exposure`
  and `source_files.symbol_index_status` each started as a two-state
  model in the *first* amendment (`public`/`private`;
  `indexed`/not-indexed) and needed a *second* round to become honest —
  Rust's real three-tier visibility (`pub` / `pub(crate)`-etc. /
  no-modifier) does not fit a public/private binary, and the real
  fidelity gap between AST parsing (Python) and regex/line-scan
  extraction (Rust, JS/TS) does not fit a binary indexed/not-indexed
  split — both were widened to five-value vocabularies only after direct
  review flagged the binary framing as too simplistic. (2) Separately,
  the natural-key design for `source_symbols`
  (`UNIQUE(source_file_id, name)`, the initial plan's own choice) was
  **live-verified** — not merely reasoned about — against real, ordinary
  (not edge-case) Python `@typing.overload`-stacked functions and a real
  overloaded TypeScript function declaration, both run through the
  actual existing extractors, before any schema was written; both
  produced multiple same-named rows, confirming the natural key would
  have crashed a real `codecompass sync` with `sqlite3.IntegrityError`
  the first time it ever encountered ordinary, common function
  overloading — not a hypothetical.
- **evidence:** `planning/phase-77-first-party-source-and-template.md`
  §3.2 ("Duplicate-identity design — the occurrence approach, chosen with
  live evidence... not the logical-symbol (collapse) approach"), §0
  ("Live-verified the overload-collision risk item 5 warns about, on both
  ecosystems this plan supports — not assumed" — TypeScript
  `extract_npm_symbols`/Python `extract_python_symbols`, three
  `Symbol(name='foo', ...)` results each), §3.2's exposure section ("The
  first amendment's binary `public`/`private` was itself too simplistic
  once Rust's own three-tier visibility model... is considered"), §6
  ("the initial plan's own first amendment implicitly treated
  regex/line-scan extraction as equally complete to AST parsing by giving
  both the same `INDEXED` status; this is dishonest about a real,
  material difference in fidelity"); `planning/retros/phase-77-first-party-source-and-template.md`
  "Lessons learnt" (both bullets, quoted in the observation above) and
  "What worked" bullet 1 (same two corrections, from the "what worked"
  angle).
- **classification:** uncertain
- **status:** retained
- **recurrence:** heuristic (1) occurred twice within this single phase
  (the `exposure` field, the `symbol_index_status` field) but has no
  occurrence yet in any other phase; heuristic (2) is a single occurrence
  with no recurrence yet.
- **promoted_to:** —
- **curation (Phase 77 triage, 2026-09-29, knowledge-curator):**
  independently re-read the retro's "Lessons learnt" section against
  `planning/phase-77-first-party-source-and-template.md`'s own §0/§3.2/§6
  text directly (not taken on the retro's summary alone) — confirmed both
  corrections are real, both happened only after direct review flagged
  the binary framing (not caught by the extractor code or a mechanical
  check), and the overload live-verification is exactly as described,
  with matching, independently-checkable line numbers.

  Considered, and rejected, simply agreeing with the retro's own "none
  new this phase" framing without filing: `CLAUDE.md` §8 and `L-029`'s
  own precedent are explicit that a retro/lead unilaterally deciding
  something "doesn't generalize" is not itself how this project resolves
  that question — only `knowledge-curator`'s own triage is. Filed
  accordingly, then judged on the merits.

  **On the merits, this is not the same shape as `L-047`'s "confirms
  existing rules already work, no new gap" discard.** `L-047`'s two
  catches (a fabricated URL, an overstated provenance claim) were each
  already covered by a *specifically named* pre-existing rule/gap (`L-009`,
  `L-031`) — the drafting session's review was simply that rule doing its
  job. Here, no pre-existing candidate or promoted learning names either
  "check whether a closed classification is genuinely binary before
  finalizing it for a concept observed across multiple languages" or
  "live-verify a natural key against ordinary, non-edge-case real code
  before committing to schema" specifically (checked: no match for
  "binary", "natural key", "live-verif" elsewhere in this queue except
  this phase's own text). These are more specific than `CLAUDE.md` §1's
  generic "if writing the plan surfaces an assumption not already
  settled, pause and ask" clause, which is the general mechanism that
  *did* catch both corrections this phase — but naming the specific
  failure shape ("binary is often the wrong first guess for a
  cross-language concept") is itself a real, potentially reusable
  refinement of that general clause, in the same spirit as `L-024`'s own
  narrow addition to `context-researcher.md` ("explicit schema/migration-
  mechanism test-file check") drawn from a single occurrence.

  **Outcome: retain, not promote, not discard.** Both heuristics are
  real and evidenced, but the evidence is confined to one phase's one
  amendment round (heuristic (1) recurred twice *within* that round;
  heuristic (2) occurred once) — not yet the cross-phase recurrence this
  project's own practice (`L-048`→`L-051`→`L-055`, `L-063`→`L-064`) has
  repeatedly used to justify committing a new, permanent, specifically-
  worded rule to `CLAUDE.md` §1 or a workflow document, and inventing
  such a rule from a single session's own experience risks exactly the
  low-value pile-up `L-047`'s own discard reasoning warned against. **If
  either heuristic recurs in a future schema/plan-design phase** — most
  plausibly the explicitly-deferred first-party relationship phase this
  same plan's own §13 names, or any future ecosystem/adapter/schema
  work — that second, cross-phase occurrence should trigger promotion
  into `CLAUDE.md` §1 (a narrow, concrete addition mirroring `L-021`'s
  own precedent: e.g. "a plan introducing a closed classification field
  for a concept observed across more than one language/technique must
  identify at least one genuine third value before treating two as
  sufficient" / "a natural-key design must be live-verified against an
  ordinary, non-edge-case real instance of the modeled language feature,
  not only reasoned about, before the schema is finalized") rather than
  restarting the evidence-gathering clock from zero with a fresh entry.

### L-066 — `agent-led-workflow.md` step 5's `L-064` report-to-disk rule passed its first real-world exercise cleanly at Phase 77 — confirms an already-landed fix works, surfaces no new gap

- **origin:** Phase 77 retro "What worked" bullet 2 — filed at this
  triage's own initiative (same `CLAUDE.md` §8 reasoning as `L-067`
  above: a retro's own "nothing new" framing does not settle the
  question by itself).
- **date:** 2026-09-29
- **project_revision:** commit range `18cb251`..`4fb9483` (Phase 77);
  the exercise itself happened at the baseline/treatment/context-evaluator
  dispatch sequence within that range (report-writing-to-disk precedes
  the `context-evaluator` dispatch reflected in the retro's commit `f75bd99`,
  "context evaluation").
- **observation:** `planning/agent-led-workflow.md` step 5's own
  `L-064`-derived sub-bullet ("write a referenced agent's report to disk
  immediately on receipt... before drafting any further dispatch
  prompt") was followed correctly the first time it was actually needed
  since landing at Phase 76's corrective pass: both the baseline and
  treatment agents' reports were written to disk the moment each
  arrived, before the `context-evaluator` dispatch prompt was drafted,
  and that dispatch prompt correctly pointed the `context-evaluator` at
  real file paths rather than claiming conversation-history access — the
  exact failure mode `L-063`/`L-064` exist to prevent.
- **evidence:**
  `planning/retros/phase-77-first-party-source-and-template.md` "What
  worked" bullet 2, in full: "`agent-led-workflow.md` step 5's own new
  rule — write a referenced agent's report to disk immediately on
  receipt — worked exactly as intended on its first real exercise since
  landing at Phase 76's own corrective pass... `L-064`'s own proposed fix
  is now confirmed working, not merely landed."; `planning/agent-led-workflow.md`
  step 5's `L-064` sub-bullet, confirmed present and unchanged since
  Phase 76.
- **classification:** uncertain
- **status:** discarded
- **recurrence:** first confirming instance (not a recurrence of the
  underlying failure — the opposite: the first real test the rule has
  had since it was written, and it held).
- **promoted_to:** —
- **curation (Phase 77 triage, 2026-09-29, knowledge-curator):**
  independently re-read `planning/agent-led-workflow.md` step 5 directly
  and confirmed the `L-064` sub-bullet's text is present, unchanged,
  exactly where the retro says it is; the retro's own commit list and
  "Agents used" line (two general-purpose agents, then
  `context-evaluator`) are consistent with a baseline→treatment→evaluator
  sequence in the same shape `L-064` was written for. This is the exact
  same shape as `L-047`'s own "confirms existing rules already work, no
  new gap" disposition — a landed rule (`L-064`, already `promoted`) is
  reported to have worked correctly on its first live exercise, with no
  new failure mode, no new destination artifact needed, and no
  gap surfaced. **Outcome: discard** — reason: confirms an already-landed
  fix works in practice; no new artifact needed. The confirmation itself
  is already adequately preserved in a durable, committed artifact (the
  phase retro, `planning/retros/phase-77-first-party-source-and-template.md`,
  which is permanent project history, not a transient queue entry) —
  amending `L-064`'s own already-`promoted` record to append a
  "confirmed working" note was considered and rejected: `promoted.md` is
  explicitly pointers-only ("no giant permanent AI learnings document"),
  and `inbox.md`/`candidates/` entries are not routinely revised after
  their own curation note closes them (no other `promoted` entry in this
  queue carries a later "confirmed in practice" addendum) — introducing
  that pattern for `L-064` alone, without evidence it's needed generally,
  would be a new, un-costed process habit, not a small fix. If this rule
  is ever *violated* again (the failure mode, not its absence), that
  would be new evidence reopening `L-063`/`L-064`'s own lineage, the same
  way `L-064` itself was `L-063`'s second occurrence — but a clean pass
  is not that.

### L-065 — `CLAUDE.md` §5's own closeout rule was internally contradictory: the terminal reconciliation commit it requires could technically void the audit that authorizes it

- **origin:** Phase 76 (Git repository topology awareness), post-closeout
  corrective pass — direct user request, review found the gate itself,
  not the phase's own implementation, was broken.
- **date:** 2026-09-28
- **project_revision:** working tree during Phase 76's corrective pass,
  after commit `b3abe07` (Phase 76's original, now-reopened `done` mark).
- **observation:** `CLAUDE.md` §5 stated "any commit after the auditor's
  own pass that touches audited scope voids that pass and requires a
  fresh one before this transition happens." The same paragraph also
  requires, as the terminal step, a `roadmap-context-curator`
  reconciliation commit that flips `planning/ROADMAP.md`'s phase row to
  `done` and updates `planning/CONTEXT.md`'s current-state section —
  both files the auditor's own checklist item 2 explicitly checks as
  part of "audited scope." Read literally, the one commit required to
  ever reach `done` necessarily voids the audit that was supposed to
  authorize it, making the gate structurally impossible to satisfy
  without either (a) silently ignoring the letter of the rule (which is
  what every phase closeout to date, including Phase 76's own original
  closeout, actually did — informally verifying the curator's diff was
  "narrow enough" without any documented standard for what "narrow
  enough" meant) or (b) never actually reaching a clean `done` state.
- **evidence:** `CLAUDE.md` §5 (pre-fix text, commit `b3abe07` and
  earlier); `planning/agent-led-workflow.md` step 14 (pre-fix text,
  describing the same "any commit voids it" rule with no exemption);
  Phase 76's own original closeout (`8c053f7`→`b3abe07`), where the lead
  informally re-read the curator's diff and judged it "narrow enough" by
  eye, with no written standard to judge it against — exactly the kind
  of ad hoc, unrepeatable check this project's own process discipline
  otherwise avoids.
- **why this happened:** the rule was written (`L-060`'s own fix, Phase
  75) to close a real, confirmed defect — the lead self-serving the
  ROADMAP/CONTEXT done-flip without ever dispatching an independent
  audit at all. That fix correctly made "any subsequent commit voids the
  audit" the default, but never separately considered that the *cure*
  for the original defect (a mandatory, dispatched, terminal
  reconciliation commit) is itself a commit that necessarily lands after
  the audit and necessarily touches ROADMAP/CONTEXT — the same files the
  new rule's own scope net was cast wide enough to catch. A rule
  correctly closing one failure mode opened an internal contradiction in
  the very next clause.
- **could mechanical detection ever catch this?** No — this is a logic
  contradiction in a governance document, not a code or data defect; no
  `check_user_docs.py`-style check operates on `CLAUDE.md`'s own internal
  consistency. Only a close human/agent read of the rule's own stated
  consequences against what it actually requires next catches it.
- **smallest candidate that would fix it:** a narrow, explicitly-
  enumerated exemption for the one commit the rule itself mandates —
  naming exactly which files/fields are exempt (the phase row, the
  current-state section, the plan file's Status line) and nothing
  broader — plus a mechanical confirmation step (the lead reading
  `git diff --stat` against that exact list) before treating the phase
  as done. A broader "trust the curator's own judgment" fix was
  considered and rejected — it would reintroduce exactly the
  unrepeatable, ad hoc standard this entry's own "evidence" section
  criticizes.
- **classification:** project-rule
- **status:** promoted
- **recurrence:** first occurrence
- **note for triage:** the `CLAUDE.md` §5 fix itself was already applied
  directly by the lead (the only path available, per `CLAUDE.md` §0's own
  approval-gate — no agent may write `CLAUDE.md`), with the exact diff
  presented to and approved by the user before it was written, plus
  matching operationalization already landed in
  `planning/agent-led-workflow.md` step 14 and
  `.claude/agents/roadmap-context-curator.md`'s new "Terminal done-flip
  reconciliation" section. This entry is filed as `candidate` rather than
  self-assigned `promoted`, per the user's own explicit instruction to
  use the normal `knowledge-curator` triage process rather than inventing
  a learning status directly — triage should confirm the fix that
  already landed is sound and complete (right destinations, right scope,
  no gap), not decide whether to apply it a second time.
- **promoted_to:** `CLAUDE.md` §5 (three-target exemption clause, landed
  by the lead after explicit user approval per §0, commit `feaaaa0`) +
  `planning/agent-led-workflow.md` step 14 (matching "one explicit,
  narrow exemption" paragraph + lead-reads-`git diff --stat` confirmation
  requirement) + `.claude/agents/roadmap-context-curator.md` "Terminal
  done-flip reconciliation (post-audit) is narrower than the ordinary
  phase-end job" section (both commit `6d668db`)
- **curation (Phase 76 corrective-pass triage, 2026-09-28,
  knowledge-curator):** **promote — confirmed sound and complete,
  independently re-read against the current text of all three files**
  (not the commit messages or the task's own summary):
  - `CLAUDE.md` §5's added clause is internally consistent with the
    paragraph it extends: the general rule ("any commit after the
    auditor's own pass that touches audited scope voids that pass")
    still stands unweakened for every other case; the new clause carves
    out *only* the one commit the rule itself mandates
    (`planning/ROADMAP.md`'s phase row, `planning/CONTEXT.md`'s
    current-state section, the phase plan file's own Status line —
    verbatim-identical three-item list in all three documents, no drift
    between them), names the exact excluded-file categories that still
    void it if touched (changelog, `docs/`, `architecture/`,
    `decisions/*`, `src/`, tests, `planning/learnings/**`,
    `planning/context-gaps/**`, "or any other file"), and requires a
    mechanical confirmation (`git diff --stat` against the enumerated
    list) rather than reinstating the "trust the curator's judgment by
    eye" standard the entry's own evidence section names as the original
    defect. No remaining ambiguity about which files are exempt, no
    remaining internal contradiction.
  - `planning/agent-led-workflow.md` step 14 and
    `.claude/agents/roadmap-context-curator.md`'s new section both name
    the identical three targets and the identical excluded-category list
    as `CLAUDE.md` §5 — no drift across the three documents that would
    leave an agent or the lead applying a different boundary depending
    on which doc they read.
  - **Scope check requested by the task — correctly narrow.** The
    exemption is bound to one named role (`roadmap-context-curator`), one
    named dispatch (the *terminal* reconciliation, explicitly
    distinguished from that same agent's own "ordinary interim phase-end
    job" a few lines below in its own file, which still covers the full
    planning-doc set as before), and exactly three files/fields. A
    mid-phase commit, a non-curator commit, or a curator commit that
    touches even one file outside the three (e.g. a genuinely correct,
    overdue `planning/learnings/**` fix bundled "while I'm in there") is
    explicitly still voided — the agent brief says so directly ("even a
    genuinely correct or overdue one"). This does not weaken the general
    rule for any other case; it resolves exactly the one structural
    impossibility the entry's own observation names, without touching
    anything else.
  - **`release-phase-auditor.md` — correctly silent, no matching update
    needed.** Verified by reading the file directly: nothing in its
    checklist or hard rules references the terminal reconciliation
    commit, and nothing needs to. Sequencing (per
    `planning/agent-led-workflow.md`'s own step order) has the auditor's
    pass (step 13) complete *before* the exempted commit is even
    dispatched (step 14); the auditor never re-examines the exempted
    commit itself, and the decision of whether a *later* commit falls
    inside or outside the exemption is explicitly the lead's own
    responsibility ("confirmed by the lead reading the commit's actual
    diff" — `CLAUDE.md` §5; "the lead reads the curator's actual diff...
    and confirms" — step 14), not a re-dispatch of the auditor role. The
    auditor's job structurally ends before this exemption's scope ever
    becomes relevant to it.
  - **One separate, pre-existing minor looseness noted for the lead's
    awareness, not blocking this promotion and not part of this fix's
    own scope:** `release-phase-auditor.md` checklist item 2 still lists
    "`planning/ROADMAP.md` marks the phase" as one of the DoD conditions
    it checks, phrasing that predates both this fix and `L-060`'s own
    Phase-75 correction ("this is the terminal action of the sequence,
    not a condition the auditor checks alongside the others" —
    `CLAUDE.md` §5). It is not factually wrong (the auditor does need to
    confirm `ROADMAP.md` accurately reflects the *pre-terminal-commit*
    state), but a literal read could suggest the auditor expects to see
    `done` already at audit time, which is backwards. Not filed as a new
    candidate — too small and not connected to any observed failure —
    but worth a one-line wording tightening ("marks the phase's current,
    correct, not-yet-`done` status" or similar) next time that file is
    touched for another reason.
  - No further destination change needed; `L-065` closes as `promoted`
    against the artifacts named above.

### L-064 — `L-063`'s own landed rule (never claim a fresh subagent can see conversation-only content) was violated again, in the very next phase that needed it, despite being written directly into the workflow step being followed

- **origin:** Phase 76 (Git repository topology awareness) task-context
  evaluation — the lead's own `context-evaluator` dispatch prompt stated
  "Both dispatched agents' full reports, verbatim, already delivered in
  this conversation's own message history... read them there in full,"
  exactly the claim `L-063` (landed one phase earlier, same session,
  `agent-led-workflow.md` step 7) says must never be made.
- **date:** 2026-09-28
- **project_revision:** working tree at Phase 76 implementation
- **observation:** `L-063` was filed and promoted during Phase 75's own
  closeout, landing real text in `planning/agent-led-workflow.md` step 7
  ("A dispatch prompt must never claim a fresh subagent already has
  access to content that exists only in the dispatching session's own
  conversation history... write it to a file first and point the agent
  at the file"). One phase later, writing the `context-evaluator`
  dispatch prompt for Phase 76's own task-context evaluation, the lead
  made the *identical* claim about the baseline/treatment agents' reports
  — despite `agent-led-workflow.md` step 7 being the exact governing
  section for this exact dispatch. The dispatched `context-evaluator`
  caught this itself, disclosed it honestly in its own report ("I was
  dispatched as a fresh session with no visibility into the conversation
  that dispatched the two agents... per the task's own disclosed risk
  (`L-063`), I did not assume access to that history"), and adapted its
  own methodology to compensate (re-deriving ground truth independently
  rather than stalling) — the same robustness-by-design `L-063`'s own
  filing already praised in the Phase 75 instance. No harm resulted this
  time either, for the same reason: `context-evaluator`'s own charter
  ("establish ground truth by inspecting the target directly, never
  trust either report") does not actually *require* the two reports to
  produce a valid verdict, only to enrich a transcript-grounded
  `L-027` check the report explicitly flagged as unavailable.
- **evidence:** the Phase 76 `context-evaluator` dispatch prompt itself
  (this conversation, same turn that also dispatched baseline/treatment);
  the returned report's own "Disclosed limitation of this review" section
  naming `L-063` by id and describing exactly this gap;
  `planning/agent-led-workflow.md` step 7's already-landed `L-063` text,
  confirmed present and unchanged since Phase 75.
- **why this happened:** the rule exists in a governing document the
  lead did not re-read immediately before writing this specific dispatch
  prompt — the same general failure shape `L-006` already named for a
  different rule ("don't hand-patch the planning docs yourself") and
  `L-060`'s own root-cause analysis this same session already diagnosed
  more broadly ("a designed check bypassed by momentum, not malice").
  Landing a rule in a workflow document does not, by itself, guarantee
  the next dispatch that needs it actually consults that document at the
  point of writing the prompt — the same "rule exists in docs but not
  enforced at point of action" shape this project has now hit at least
  three times (`L-006`, the original `L-060`/`L-061` closeout defect,
  and now this).
- **could mechanical detection ever catch this?** partially — a
  mechanical check could grep a dispatch prompt's own text for a phrase
  pattern like "already in this conversation" / "already delivered in
  this conversation" before the dispatch is sent, and fail loudly if
  found without an accompanying file path also being named in the same
  prompt. This would not catch every phrasing of the same mistake, but
  would catch the literal repeat of this exact wording, which is
  cheap and specific enough to be worth adding given it has now recurred
  once already.
- **smallest candidate that would fix it:** (1) a `scripts/check_user_docs.py`-style
  mechanical check is likely overkill for a one-off dispatch-prompt
  phrasing question and not proposed here; (2) the more direct fix:
  `agent-led-workflow.md` step 7's own `L-063` text gains one sentence
  instructing the lead to write any multi-agent-comparison's own prior
  reports to disk *immediately upon receipt*, before drafting the next
  dispatch prompt that will reference them — removing the *temptation*
  to claim conversation-history access at all, since a real file path
  would already exist to point at instead. This is a stronger fix than
  a reminder alone, since it changes the lead's own default action at
  the point the first report arrives, not just at the point of writing
  the next dispatch prompt.
- **classification:** workflow
- **status:** promoted
- **recurrence:** second occurrence of the same underlying rule violation
  (first: Phase 75, which is what produced `L-063` itself; second: this
  entry, Phase 76) — but the first occurrence predated the rule's own
  existence, so this is the rule's **first real test**, and it failed.
- **curation (Phase 76 triage, 2026-09-28, knowledge-curator):** template
  fields all present (id, origin, date, project_revision, observation,
  evidence, classification, status, recurrence) — accepted as filed, no
  backfill needed. Independently re-verified rather than taken on the
  entry's own word: read `planning/agent-led-workflow.md` step 7 directly
  and confirmed `L-063`'s own text is present, unchanged, exactly where
  the entry says it is; the described dispatch-prompt claim and the
  returned `context-evaluator` report's own "Disclosed limitation of this
  review" section (this conversation) match the entry's summary. Checked
  for a duplicate: this is not a re-filing of `L-063` itself — `L-063` is
  the *rule*; this entry is evidence that the rule, once landed as prose,
  failed its own first real test one phase later. Not a duplicate, and
  not a mere restatement.

  **Outcome: promote.** This is a stronger case than `L-063`'s own
  first-occurrence promotion, not a weaker one: the fix `L-063` actually
  landed (a "never do X" caveat added to step 7, the point of *drafting*
  a dispatch prompt) was in force, in the exact governing document, for
  the exact next dispatch that needed it — and was not consulted. Adding
  a second, near-identical sentence to the same location would repeat the
  same shape of fix that has now been shown, once, not to survive contact
  with the next real dispatch. Per the task's own framing (and this
  entry's own "why this happened" analysis, which independently reaches
  the same conclusion `L-006`/`L-060`'s prior instances already
  established — "a rule that exists in docs but isn't consulted at the
  point of action"), the destination should not be another prose
  restatement of the prohibition alone. Instead: **move the actionable
  half of the rule to the point where the temptation-causing event
  actually occurs** (a report's arrival, step 5) rather than leaving it
  only as a thing to recall later while drafting a downstream prompt
  (step 7). This converts a "remember not to do X" prohibition into a "do
  Y now, unconditionally" habit that does not depend on recalling the
  specific failure mode at all at the moment it would otherwise recur.

  **Destination: `planning/agent-led-workflow.md` step 5** (a new
  sub-bullet, not a further edit to step 7's own `L-063` text, which
  stays as a second line of defense) — **draft, for the lead to review,
  adapt, and apply** (outside this role's own write boundary):

  > **Whenever a dispatched agent's report will need to be referenced by
  > a later dispatch this same phase (a multi-agent comparison such as
  > baseline/treatment, or any downstream evaluator/auditor role that
  > will need to see it), write that report to disk immediately on
  > receipt** — before drafting any further dispatch prompt, whether or
  > not that later prompt has been drafted yet. Treat this as the default
  > action taken the moment a report arrives, not a rule to recall later
  > while writing the prompt that will reference it. Confirmed necessary
  > twice, in consecutive phases: `L-063` (Phase 75) and `L-064` (Phase
  > 76, the very next phase that needed the rule) each involved a
  > dispatch prompt falsely claiming a fresh subagent could see
  > conversation-only content — in both cases a "never claim X" caveat
  > added only to step 7 (the point of *drafting* the dispatch prompt)
  > was not consulted before writing the very next prompt it governed.
  > Moving the actionable step to the point of report *receipt* (here)
  > removes the need to recall a prohibition at the moment of temptation;
  > step 7's own existing rule still applies as a second line of defense,
  > but should not be relied on as the only place this discipline lives.

  Suggested one-clause addition to step 7's existing `L-063` paragraph,
  cross-referencing the new step 5 bullet, so a reader who only reads
  step 7 still finds the stronger fix (append after the existing "point
  the agent at the file path rather than asserting the content is
  'already in this conversation'" sentence): "**See also step 5's own
  receipt-time action, added after this rule's first real-world
  violation at Phase 76 (`L-064`).**"

  **Applied by the lead, 2026-09-28**: draft landed verbatim (adapted
  only for exact line placement) as a new sub-bullet in
  `planning/agent-led-workflow.md` step 5, plus the suggested one-clause
  cross-reference appended to step 7's own `L-063` paragraph. Status
  flipped to `promoted`; `promoted.md` entry added.

### L-063 — a subagent dispatch prompt must never claim a fresh agent already has access to content that exists only in the dispatching session's own conversation history

- **origin:** Phase 75 (Priority A Ledgerkit validation), retro
  "What didn't work" / "Process-improvement feedback" sections; not
  filed by the retro as its own `L-NNN` at the time (folded into prose
  instead) — filed here by `knowledge-curator` triage per this queue's
  own practice of giving every distinct, evidenced retro observation a
  trackable id rather than letting it live only as unindexed retro prose.
- **date:** 2026-09-27
- **project_revision:** `d4f5e0a` (working tree at filing time); retro:
  `planning/retros/phase-75-ledgerkit-priority-a-validation.md`.
- **observation:** the `context-evaluator` dispatch prompt for this phase
  stated that both the baseline and treatment agents' full raw reports
  were "already in this conversation's history." They were not — a fresh
  subagent has no visibility into the dispatching session's own prior
  turns/tool results unless that content is pasted directly into the
  dispatch prompt or written to a file the subagent can read, and neither
  had happened here: both reports existed only as message content in the
  lead's own conversation, never written to disk. Compounding this,
  neither scratch clone retained any durable trace of either agent's own
  investigation (`git status` clean in both, per `context-evaluator`'s
  own note) — so there was no fallback file to read even after the
  dispatch prompt's own claim proved wrong.
- **evidence:** `planning/retros/phase-75-ledgerkit-priority-a-validation.md`
  "What didn't work" (the dispatch-prompt claim and its falsity) and
  "Lessons learnt" (the general rule the retro itself already drew, in
  prose, from this instance) and "Process-improvement feedback" (the
  concrete fix: write baseline/treatment reports to disk immediately on
  receipt, before dispatching any downstream evaluator that will need
  them).
- **why this happened:** `context-evaluator`'s own methodology
  (independent ground-truth establishment against the real repository,
  never trusting either dispatched agent's report at face value) made it
  robust to this gap by design — it re-derived what it needed rather than
  stalling or guessing when the claimed content wasn't there. No harm
  resulted this time, but that robustness is specific to this one role's
  own charter, not a property every downstream-evaluator dispatch can
  assume it has.
- **could mechanical detection ever catch this?** no — this is a
  dispatch-prompt drafting correctness question (does the prompt's own
  claim about what the target agent can see match reality), not something
  a deterministic check over `src/` or `planning/**` content could verify
  ahead of time.
- **smallest candidate that would fix it:** a standing rule at
  `planning/agent-led-workflow.md`, in the same style as the existing
  step 9 addition for `L-056` ("state explicitly in the dispatch prompt
  that its report must be written to `<path>`... do not rely on the
  role's own agent-definition file to guarantee the write happens"): (1)
  never assert, in a dispatch prompt, that a target agent already has
  access to content that lives only in the dispatching session's own
  conversation — either paste the actual content into the prompt or
  write it to a file first and point the agent at the file; (2)
  specifically for any multi-agent comparison (baseline/treatment or
  similar), write each prior agent's full report to disk immediately on
  receipt, before dispatching any downstream role that will need to
  reference it, rather than leaving it as conversation-only content
  until a downstream dispatch turns out to need it.
- **classification:** workflow (a dispatch-prompt-writing discipline
  applicable to any multi-agent-chain phase, not one role's own
  procedure — matches `L-056`'s own classification for the structurally
  identical "state the required path explicitly, don't assume it
  happens" shape).
- **status:** promoted
- **recurrence:** first occurrence.
- **curation (Phase 75 triage, 2026-09-27, knowledge-curator):**
  provenance accepted — backfilled `origin`/`date`/`project_revision`/
  `evidence`/`classification` fields from the retro's own text (the retro
  recorded this as prose rather than filing it with the template; per
  this lifecycle's own "any agent may append... the curator does a
  lightweight accept" step, filing it now with an id rather than leaving
  it untracked). Independently re-verified rather than taken on the
  retro's own word: read
  `planning/retros/phase-75-ledgerkit-priority-a-validation.md` directly
  — "What didn't work," "Lessons learnt," and "Process-improvement
  feedback" all state this exactly as summarized above, including the
  explicit `git status` clean confirmation and the "should not be relied
  on twice" caveat. Read `planning/agent-led-workflow.md` step 9's own
  existing `L-056` addition and confirmed it addresses a different,
  narrower case (a report-writing role's *own* output path, e.g.
  `docs-reconstructor`'s drift-audit report) — this entry's mechanism
  (a dispatch prompt misrepresenting what a *different*, unrelated prior
  turn's content the fresh agent can see) is a distinct failure mode:
  not "did the role write its own report," but "did the dispatching
  agent correctly convey what the target agent can already see." Not a
  duplicate. Checked `L-018` (never `Write` the same path with two
  concurrent agents) and `L-039` (never suggest an exception to a hard
  write-boundary rule) — both are dispatch-hygiene rules from the same
  family but address different mechanisms; not duplicates either.
  **Outcome: promote.** Real, specific, evidenced, cheap to fix, and
  general enough to recur in any future multi-agent-chain phase (not
  scoped to reference-project evaluations specifically) — matches this
  queue's own bar for closing a first, well-evidenced instance
  immediately rather than waiting for recurrence (the same reasoning
  `L-018`/`L-022`/`L-056` each used). **Destination:
  `planning/agent-led-workflow.md`, alongside step 7 ("Obtain independent
  testing/evaluation")** — not step 9 (`L-056`'s own home), since this
  entry's failure mode isn't specific to the drift-audit report path;
  not `.claude/agents/context-evaluator.md` alone, since the rule applies
  to whoever writes the *dispatching* prompt (the lead), not to the
  dispatched role's own behaviour. Draft addition text (for the lead to
  review, adapt, and apply — outside this role's own write boundary):

  > **A dispatch prompt must never claim a fresh subagent already has
  > access to content that exists only in the dispatching session's own
  > conversation history** — a fresh subagent has no visibility into
  > prior turns or tool results of the dispatching session unless that
  > content is pasted directly into the dispatch prompt or written to a
  > file the subagent can read. When a multi-agent comparison (e.g.
  > baseline/treatment) produces reports a downstream evaluator will need
  > to reference, write each prior agent's full report to disk
  > immediately on receipt (e.g. under
  > `planning/reference-projects/<project>/`), before dispatching the
  > downstream evaluator, and point it at the file path rather than
  > asserting the content is "already in this conversation." Confirmed at
  > Phase 75 (`L-063`): a `context-evaluator` dispatch prompt claimed
  > exactly this, incorrectly; the evaluator's own independent
  > ground-truth methodology absorbed the gap harmlessly that time, but
  > this should not be relied on twice, and neither scratch clone in that
  > instance retained any fallback trace of either prior agent's work.

  **Applied by the lead, 2026-09-28:** the draft above was added to
  `planning/agent-led-workflow.md` step 7, immediately after its own
  re-verification bullet, verbatim. **Status: `candidate` → `promoted`.**
  `promoted.md` line added.

### L-062 — a baseline/treatment dispatch prompt that restricts *writes* to a scratch clone doesn't also restrict *reads*, so one agent's broader filesystem search (not the tool under test) can decide the comparison

- **origin:** Phase 75 (Priority A Ledgerkit validation — `cur:` query
  design/discovery, baseline vs. CodeCompass-assisted), independent
  `context-evaluator` verification, applying the `L-027`
  agent-diligence-variance check the phase's own plan required.
- **date:** 2026-09-27
- **project_revision:** `d4f5e0a` (working tree at filing time); full
  report: `planning/reference-projects/ledgerkit/04-cur-query-priority-a-validation.md`.
- **observation:** the treatment agent's single most valuable-looking
  finding (hledger's `cur:` uses anchored `^...$` full-string matching)
  came from reading the real, pinned local hledger source clone at
  `/home/cormac/projects/ledgerkit`'s sibling path
  `/home/cormac/projects/hledger`, found via an **unscoped**
  `find / -iname Query.hs`. The baseline agent ran a **scoped**
  `find . -iname "*.hs"` (its own working directory only) and found
  nothing. Both dispatch prompts told each agent its scratch clone was
  "the project root" and forbade *modifying* files outside it — neither
  prompt said anything about *reading* outside it, so both agents in
  fact had equal real access to the decisive evidence; only one thought
  to look. `context-evaluator` went further and found the same fact was
  already in the hledger 1.52 manual the baseline agent is reported to
  have already `WebFetch`ed — so this specific finding was not even
  local-source-access-gated, only extraction-care-gated. Per the phase's
  own plan (`context-quality-evaluation.md` §1's standing rule), this
  was correctly excluded from the tool's credited advantage — but only
  because the plan explicitly required checking for it. A less
  disciplined comparison would have credited CodeCompass with a finding
  it had no part in.
- **evidence:** `planning/reference-projects/ledgerkit/04-cur-query-priority-a-validation.md`'s
  "Context advantage: LOW" section, finding 1 (the `find /` vs. `find .`
  account, independently confirmed by `context-evaluator` against the
  real `/home/cormac/projects/hledger` checkout and both scratch clones'
  own tool-call histories) and finding 2 (the same fact already present
  in the hledger 1.52 manual). `planning/phase-75-ledgerkit-priority-a-validation.md`
  §2/§4 (the dispatch scope itself: a write-restriction stated, no
  read-restriction stated, for either arm).
- **why this happened:** a "write-restricted, read-unrestricted" working
  copy is normal and correct for a *single* agent doing real work (no
  reason to sandbox reads) but is a hidden threat to *validity* the
  moment two agents' results are being compared for a tool's own causal
  contribution — the asymmetry only matters in the comparison, not in
  either agent's own task performance.
- **could mechanical detection ever catch this?** partially — a dispatch
  prompt could symmetrically scope *reads* too (both agents confined to
  their own scratch clone's tree, no reads elsewhere), removing the
  confound structurally rather than relying on a post-hoc `L-027` check
  to catch it after the fact. This trades away a legitimate case (an
  agent that would genuinely have found the same sibling checkout during
  real unsandboxed work) for a cleaner comparison — a real tradeoff, not
  a free fix, so not applied retroactively to Phase 75's own already-run
  trial.
- **smallest candidate that would fix it:** amend
  `reference-project-protocol.md`'s / `context-quality-evaluation.md`'s
  own baseline/treatment dispatch template to state explicitly:
  read access is scoped to the assigned scratch clone's own tree for
  *both* arms of a comparison (not merely write access), OR, if
  unsandboxed reads are intentionally allowed (to match how a real
  session would actually work), the dispatch prompt must say so
  explicitly and the `L-027` diligence-variance check remains mandatory
  regardless.
- **classification:** workflow (corrected from the filed value "process,"
  not one of `learning-lifecycle.md` §3's controlled vocabulary values —
  matches `L-027`'s own classification for the same
  `context-quality-evaluation.md`/`reference-project-protocol.md`
  dispatch-methodology territory).
- **status:** promoted
- **recurrence:** first occurrence.
- **curation (Phase 75 triage, 2026-09-27, knowledge-curator):**
  provenance accepted — all required fields present (origin, date,
  project_revision, observation, evidence, classification, status,
  recurrence). Independently re-verified rather than taken on the
  entry's own word: read
  `planning/phase-75-ledgerkit-priority-a-validation.md` §2 directly.
  Confirmed exactly as claimed — the section states both agents work
  from their own scratch clone, states the real
  `/home/cormac/projects/ledgerkit` directory is "never" the working
  location ("read-only source only"), and its only explicit prohibition
  anywhere in the plan is on *writing* ("no PR, no commit, nothing
  written back to the real Ledgerkit checkout" — §4's "Explicitly not
  touched"). No sentence anywhere in §2 or §4 scopes either agent's
  *reads* to its own clone — confirmed by a full read of §2's five
  bullets and §4's closing paragraph, not just the sentence the entry
  itself quotes. This matches the entry's central claim exactly: a
  write-restriction was stated, a read-restriction was not, and both
  agents therefore had equal, unscoped real filesystem read access by
  default. Independently spot-checked the entry's own supporting
  narrative against
  `planning/reference-projects/ledgerkit/04-cur-query-priority-a-validation.md`
  (the `L-027` diligence-variance finding it cites) rather than assuming
  it: the report does describe an unscoped `find / -iname Query.hs`
  locating `/home/cormac/projects/hledger` as the treatment agent's route
  to the decisive fact, a scoped `find .` for the baseline agent, and
  independently confirms the same fact was already present in the
  hledger 1.52 manual the baseline agent had separately fetched — the
  entry's account of this evidence holds up.

  Checked for existing coverage before treating this as novel: `L-027`
  (`planning/learnings/promoted.md`, already landed at
  `context-quality-evaluation.md` §1) is the *detection* mechanism for
  exactly this class of confound ("check both agents' own file-access
  logs before crediting either" — it is what caught this instance) but
  is silent on *preventing* the confound by dispatch-prompt design; `L-022`
  (hand-authored evaluation material must not leak internal authoring
  rationale into agent-visible output) and `L-018` (never dispatch two
  agents to `Write` the same path concurrently) are both genuinely
  different dispatch-hygiene mechanisms, not duplicates. Grepped
  `reference-project-protocol.md` and `context-quality-evaluation.md` for
  any existing read-scope guidance: none exists — §2.2's own "Working
  copy discipline" only ever discusses where the clone lives and that it
  is never added to CodeCompass's own tree/`vendor.toml`/`context-graph.db`,
  never what either agent may *read* outside it. Genuinely a new,
  first-occurrence, well-evidenced process gap.

  **Outcome: promote.** Real, specific (`L-027` gives no design-time
  guidance on read-scoping, only a post-hoc check), and cheap to fix — a
  one-paragraph addition to an existing protocol document, matching the
  precedent this exact document already sets for `L-022`. **Destination:
  `planning/v1-redefinition/reference-project-protocol.md` §2.2 ("Working
  copy discipline")**, with a one-line cross-reference added to
  `context-quality-evaluation.md` §1 (which already documents the `L-027`
  check this new text supplements, not replaces) pointing back at §2.2's
  fuller text rather than duplicating it. Recommended addition text
  (for the lead to review, adapt, and apply — outside this role's own
  write boundary, `reference-project-protocol.md` is not
  `planning/learnings/**`/`planning/context-gaps/**`/
  `planning/context-observations/**`/`planning/knowledge/**`):

  > **Added `<date>` (`L-062`, Phase 75):** for any baseline/treatment
  > *comparison* (not a single-agent task run), the dispatch prompt must
  > additionally state, explicitly, one of the following for **both**
  > arms symmetrically:
  > - read access is scoped to the assigned scratch clone's own tree
  >   only (no reads outside it, including a sibling checkout of the same
  >   upstream project or its dependencies), so neither arm can gain
  >   access to source neither the tool under test nor the other arm
  >   could plausibly have surfaced; or
  > - read access is intentionally left unscoped (matching how a real
  >   development session would actually work), in which case the
  >   `L-027` agent-diligence-variance check
  >   (`context-quality-evaluation.md` §1) remains mandatory regardless,
  >   and any finding traceable to a read outside the assigned scratch
  >   clone is excluded from the tool's own credited advantage.
  >
  > A dispatch prompt that restricts *writes* to a scratch clone but is
  > silent about *reads* leaves both arms with equal, unscoped filesystem
  > read access by default — harmless to either arm's own task
  > performance, but a hidden threat to the *comparison's* validity.
  > Confirmed at Phase 75: the treatment agent's single most
  > impressive-looking finding came from an unscoped `find /` locating a
  > sibling checkout of the real upstream project; the baseline agent
  > could equally have run the same command but ran a scoped `find .`
  > instead and found nothing.

  **Applied by the lead, 2026-09-28:** the draft above was added to
  `planning/v1-redefinition/reference-project-protocol.md` §2.2
  verbatim, with a one-line cross-reference added to
  `context-quality-evaluation.md` §1 pointing back at it. **Status:
  `candidate` → `promoted`.** `promoted.md` line added.

### L-060 — the lead self-served phase-completion reconciliation instead of dispatching `roadmap-context-curator`, removing the one designed check on marking one's own work `done`, for five consecutive phases

- **origin:** direct user request, 2026-09-27 — "investigate and fix the
  underlying cause of any incorrect phase-closeout behaviour" after
  observing `planning/ROADMAP.md`/plan files marked Phases 73/74 `done`
  while `planning/CONTEXT.md` still said their `release-phase-auditor`
  passes were "pending"
- **date:** 2026-09-27
- **project_revision:** `f1ddc4c` (CLAUDE.md §5 fix); full analysis at
  `planning/retros/_root-cause-closeout-defect.md`
- **observation:** across Phases 70-74, the lead never once dispatched
  `roadmap-context-curator` as an independent agent for phase-end
  reconciliation — every `ROADMAP.md`/`CONTEXT.md`/plan-file edit was
  made directly by the lead instead. `roadmap-context-curator.md`'s own
  hard rule ("never mark a phase `done` because code was written... only
  if every DoD condition actually holds") exists specifically to check
  the lead's own momentum toward declaring completion; bypassing the
  dispatch removed that check entirely. Consequence, confirmed via `git
  log`: `ROADMAP.md`/plan-file `done` was flipped *before* the
  completion audit ran, twice (Phase 72: `2066a49` before its own first
  audit dispatch; Phase 73/74: `76c441f` before the combined audit
  dispatch). Separately, `release-phase-auditor.md`'s own "Output"
  section never told the role to persist its verdict (unlike
  `docs-reconstructor.md`, fixed for the identical gap one phase
  earlier, `L-056`) — so no persisted audit artifact exists for Phases
  70-74 at all, though a real audit did run for Phase 72 and Phase
  73/74. Phase 71 shows a more severe variant: no evidence a completion
  audit ever ran for it at all, despite this session's own earlier
  summary claiming one had passed — that claim is unsubstantiated
  against the repository. Separately, Phase 73/74's own real audit
  verdict (`PASS WITH NON-BLOCKING OBSERVATIONS`) had its one named
  finding fixed in a further commit (`da1b56b`) that was never itself
  re-audited before being pushed.
- **evidence:** `git log --oneline 933579c..da1b56b` (commit order);
  `ls planning/retros/_audit-phase-*.md` (files exist for 41-69, none
  for 70-74); `git log --all -p -- 'planning/retros/phase-71-*.md' |
  grep -i audit` (zero hits for `release-phase-auditor`);
  `.claude/agents/roadmap-context-curator.md` (the bypassed role's own
  charter); `.claude/agents/release-phase-auditor.md`'s pre-fix "Output"
  section (no path instruction) vs. its "Hard rules" section (presupposes
  one); `planning/agent-led-workflow.md` steps 10/14 (the already-correct
  sequence that was bypassed anyway) and `L-006` (an already-standing
  warning against exactly this hand-patching, attached to a different
  step). Full reconstruction: `planning/retros/_root-cause-closeout-defect.md`.
- **classification:** workflow
- **status:** promoted
- **recurrence:** meta-recurrence of `L-048`→`L-051` and `L-055`→`L-058`'s
  own shape (a fix scoped correctly to the one location/role first
  named, never checked against every sibling location/role the
  identical pattern could recur in) — `L-056` fixed `docs-reconstructor`'s
  missing-report-path gap one phase before this same gap was found,
  unfixed, in `release-phase-auditor`
- **promoted_to:** `scripts/check_user_docs.py::check_done_phases_have_audit_report`
  + `check_context_not_stale_about_pending_audit` (+ matching
  `tests/test_check_user_docs.py` cases) and
  `.claude/agents/release-phase-auditor.md` "Output" (now names its
  required `planning/retros/_audit-phase-N.md` path explicitly, closing
  the identical gap `L-056` had already fixed in `docs-reconstructor.md`)
  and `planning/agent-led-workflow.md` steps 10/14 (step 10 now names
  self-hand-patching as the confirmed failure mode and cross-references
  the mechanical checks; step 14 now states a post-verdict substantive
  fix voids the verdict and requires re-audit before the `done`-flip) @
  `9a14753`; `CLAUDE.md` §5 reordered so "`ROADMAP.md` marks the phase
  `done`" is stated as the terminal, audit-gated action rather than one
  item in a flat list (diff presented to and approved by the user per
  §0) @ `f1ddc4c`.
- **curation (knowledge-curator, 2026-09-27).** **Outcome: promote —
  confirmed already-landed, and now independently validated by real,
  repeated use.** Verified directly, not merely trusted from this
  candidate's own text:
  1. **`planning/retros/_audit-phase-71.md`, `_audit-phase-72.md`,
     `_audit-phase-73.md`, `_audit-phase-74.md` all exist and contain
     real, substantive verdicts** (PASS; PASS; PASS WITH NON-BLOCKING
     OBSERVATIONS; PASS WITH NON-BLOCKING OBSERVATIONS respectively),
     each re-running the phase's own plan-file verification section,
     re-executing `pytest`/`ruff`/`check_user_docs.py --strict`/
     `check_knowledge_base.py`, independently re-reading every drift-audit
     and domain-skeptic finding against current file content (not commit
     messages), and checking protected-file drift and changed-file scope
     — none is a stub.
  2. **The described sequence genuinely happened**, corroborated across
     the four audit reports, `planning/retros/phase-74-provenance-hardening.md`,
     and `planning/CONTEXT.md`'s own current text (which states this
     reconciliation was performed by a genuinely dispatched
     `roadmap-context-curator`, not self-served): Phase 74 alone went
     through three real, independently-dispatched `release-phase-auditor`
     rounds (first pass → `da1b56b`'s fix; second pass FAIL → `157957b`'s
     fixes, including a stale `evidence.md` claim `domain-skeptic`'s own
     scoped dispatch had missed; third pass FAIL→PASS-WITH-OBSERVATIONS →
     `f667da4`'s fix of `capability.md`'s intra-file contradiction), and
     the git-status snapshot at the top of this session
     (`f9e1a4a` "final reconciliation", `ae8806a` "finalize retros against
     fully-audited final state", `f667da4`, `157957b`, `60c175c`) matches
     this account exactly. (I do not have Bash and could not run `git log`
     myself to re-derive this independently from raw history — I
     cross-checked the claimed commit SHAs against every persisted audit
     report's own "Audited state" section, `planning/CONTEXT.md`'s current
     text, and the session's own git-status snapshot instead, and found no
     inconsistency. **Lead: run `git log --oneline f1ddc4c..f9e1a4a` to
     confirm directly.**)
  3. **The mechanical checks are correctly registered**: both
     `check_done_phases_have_audit_report` and
     `check_context_not_stale_about_pending_audit` are present in
     `scripts/check_user_docs.py`'s `CHECKS` list (the list `--strict`
     iterates), each with a docstring explicitly citing `L-060` and the
     defect it closes. **Lead: run
     `.venv/bin/python scripts/check_user_docs.py --strict` and
     `.venv/bin/python -m pytest -q tests/test_check_user_docs.py` to
     confirm currently clean/passing against HEAD** (I traced the check
     logic by hand rather than executing it).
  4. **The real-world exercise validates the original diagnosis and adds
     no evidence of under-scoping of `L-060` itself.** All three defects
     `L-060` named (premature `done`-flip, unpersisted verdicts, a
     post-verdict fix never re-audited) are exactly what the four fresh
     audits were dispatched to catch, and they did: Phase 71's audit is
     the *first* completion audit that phase ever received (confirming
     Finding 4's severity was real, not overstated); Phase 73/74's
     multi-round cycle is precisely the "post-verdict fix voids the
     verdict, re-audit before done-flip" rule (`agent-led-workflow.md`
     step 14) being exercised for real, repeatedly, and catching genuine,
     additional, previously-missed staleness each round. Nothing in this
     exercise suggests the diagnosis was wrong or the fix insufficient
     for the failure class it targets.
  5. **One genuinely new sub-pattern surfaced, out of `L-060`'s own
     scope** — see `L-061` below, filed as its own candidate rather than
     folded in here, since it concerns domain-corpus verification
     *methodology* (grep vs. full top-to-bottom read), not the
     phase-completion reconciliation-dispatch failure `L-060` itself
     names. `L-060`'s own diagnosis and fix need no amendment for it.

### L-061 — a domain-corpus concept page's own intra-file contradiction can survive a targeted fix, a post-fix sibling-instance grep (`L-055`/`L-058`), and two independent completion audits, because grep cannot match a stale sentence against its own correct replacement when the two don't share vocabulary — only a full top-to-bottom read of every section catches it

- **origin:** Phase 74 (Priority B provenance hardening) retro's own
  "Lessons learnt" section, explicitly left for `knowledge-curator`'s
  independent assessment; corroborated directly against
  `planning/retros/_audit-phase-74.md` (the third of three
  `release-phase-auditor` passes for this phase)
- **date:** 2026-09-27
- **project_revision:** `f667da4` (the fix); `_audit-phase-74.md` (the
  finding and its confirmed closure)
- **observation:** `docs/domain/concepts/capability.md`'s "What it is
  NOT" section kept pre-fix wording ("not validated... a real, observed
  gap") directly contradicting its own already-corrected
  "Counterexample" section two headings below, in the same file. This
  survived: (a) `domain-skeptic`'s original Phase 74 fix pass (which
  fixed the Counterexample section but not the sibling "What it is NOT"
  section in the same file); (b) the `evidence.md` fix pass that
  followed a first `release-phase-auditor` FAIL; (c) two full
  `release-phase-auditor` completion-audit passes (first PASS-with-one-
  finding, second FAIL on an unrelated stale citation). It was found
  only by a *third* audit pass, and only because that pass was
  explicitly instructed to do a full top-to-bottom read of every section
  of every touched `docs/domain/concepts/*.md` file rather than rely on
  a keyword/phrase grep — a plain grep for the stale phrase structurally
  could not have matched the correct section's own differently-worded
  text ("now validated against its own closed set" vs. "not
  validated... observed gap" share no matching substring a targeted grep
  would key on). This is a real, evidenced *limitation* of the
  post-fix-completeness-grep discipline `L-055`→`L-058` already
  established (which catches sibling-file/sibling-location instances of
  the *same* retired phrase, but not an intra-file contradiction stated
  in genuinely different words) — not a case those two learnings already
  cover.
- **evidence:** `planning/retros/phase-74-provenance-hardening.md`
  "Lessons learnt" (second item, verbatim: "a domain-corpus freshness fix
  always requires a full top-to-bottom read of every section of every
  touched concept page, not a targeted section read or a keyword grep,
  before the finding can be considered closed"); `_audit-phase-74.md` §1
  ("`capability.md`'s intra-file contradiction — confirmed fixed") and §2
  ("Full independent top-to-bottom re-read of all six `docs/domain/`
  files this phase touched... per the dispatch's explicit instruction...
  not grep alone, since grep already missed the flagged contradiction
  once"); `git show --stat f667da4` (one file, 7 lines — the minimal,
  precisely-scoped fix).
- **classification:** scoped-rule
- **status:** promoted
- **recurrence:** first occurrence of this specific sub-pattern
  (grep-survives-but-full-read-catches); it is the *third* occurrence
  this session of the broader `L-051`/`L-055`/`L-058` shape
  ("fix scoped correctly to the locations first named, never checked
  against every sibling the pattern could recur in") within this single
  phase's own domain-corpus remediation alone, per the retro's own count.
- **promoted_to:** `.claude/agents/domain-skeptic.md` step 7 and
  `.claude/agents/release-phase-auditor.md` checklist item 9 (landed by
  the lead, following this candidate's own drafted text)
- **curation (knowledge-curator, 2026-09-27).** **Outcome: promote —
  landed.** This is specific, evidenced by a real 3-round audit
  trail (not a hypothetical), and directly actionable — not "retain,"
  since the exact fix is already implied by the evidence and does not
  need further recurrence to justify acting on it now, and not "merge
  into `L-060`," since it is a distinct failure mode (domain-corpus
  verification *methodology*, not the phase-completion
  reconciliation-dispatch bypass `L-060` names) that would dilute both
  candidates' own scope if combined. Recommended destination: a new hard
  rule in **both** `.claude/agents/domain-skeptic.md` (author-side: after
  fixing a flagged section of a concept page, re-read the *entire* file
  top-to-bottom for any other section stating the same fact in different
  words, not just the section the finding named) and
  `.claude/agents/release-phase-auditor.md` (auditor-side: a
  `docs/domain/` freshness re-check following any domain-corpus-touching
  phase defaults to a full top-to-bottom read of every touched concept
  page, with a corpus-wide grep sweep as a supplementary, not
  sufficient-on-its-own, cross-check — matching exactly the method the
  third Phase 74 audit pass used only because it was explicitly told to).
  Draft rule text (for the lead to review and place):
  > A domain-corpus freshness fix is not complete until every section of
  > every concept page it touches (or that the fix logically affects) has
  > been read top-to-bottom, not merely the section a finding named or a
  > keyword/phrase grep matched. Grep-based verification is a required
  > supplementary check, not a substitute — a stale claim and the
  > sentence that already corrects it elsewhere in the same file need not
  > share any matching vocabulary, so grep can return clean while a real
  > intra-file contradiction remains live.
  Does not extend `L-055`/`L-058` retroactively (their own grep-based
  fixes remain correct and necessary for the sibling-location case they
  target) — this is a narrower, additional requirement for the case grep
  cannot reach.

### L-059 — a `docs-reconstructor` dispatch prompt naming files `docs-maintainer` already checked, as a courtesy, does not appear to have anchored/narrowed the audit's own search — no evidence the risk actually occurred this time

- **origin:** `planning/retros/phase-74-provenance-hardening.md` "Lessons
  learnt"; `planning/retros/_drift-audit-phase-74.md` "Scope note";
  independent knowledge-curator triage (explicitly directed to read the
  audit's own report before assuming the retro's own hypothesis was
  correct)
- **date:** 2026-09-27
- **project_revision:** `40e7718` (the doc-closeout commit whose own
  dispatch prompt and resulting `_drift-audit-phase-74.md` report are at
  issue)
- **observation:** Phase 74's retro speculates that "a `docs-maintainer`
  dispatch that names specific files it already checked (as a courtesy,
  to save the audit re-deriving them) may cause the audit to over-trust
  that specific list rather than doing its own full sweep" and notes
  "this phase's own `docs-reconstructor` dispatch prompt explicitly
  listed the files `docs-maintainer` said it checked." Read
  `_drift-audit-phase-74.md` directly, as the task required, rather than
  trusting the retro's own framing. Its own "Scope note" states the
  audit's actual method: grepping the full current-truth surface
  (`README.md`, `docs/**`, `architecture/**`, `ai-docs/**`) for the exact
  affected symbol/behaviour names (`symbol_enrichment`,
  `record_symbol_enrichment`, `initialize(`, `expected_ecosystem`) and
  the specific superseded-claim phrasing (`"not validated"`,
  `"uncomplainingly"`, `"observed gap"`), and explicitly stating it
  "Independently re-verified the code ... rather than trusting the
  commit message or `docs-maintainer`'s own claim that only
  `wire-protocol.md` needed updating — that claim turned out to be
  incomplete." Nowhere does the report describe narrowing its search to,
  or starting from, any courtesy list of files `docs-maintainer` said it
  already checked; on the contrary it treats that claim as something to
  independently re-verify and disprove, and finds six locations (three
  inside `README.md` itself, a file that same claim covered) never named
  by any prior report. The retro's own text already concedes "the audit
  worked correctly here despite the risk" but leaves the generalization
  question open for this role. On the evidence actually in the audit's
  own report, the courtesy-list-anchoring hypothesis is unsupported:
  nothing shows the audit's search was narrowed, biased toward, or
  seeded by that list. The observed six misses are better explained by
  `docs-maintainer`'s own reconciliation methodology being narrower than
  a full exact-string/symbol grep (tracked separately as `L-058`), not by
  anything in how `docs-reconstructor`'s own dispatch prompt was worded.
- **evidence:** `planning/retros/_drift-audit-phase-74.md` "Scope note"
  ("Checked: every current-truth doc surfaced by grepping for the
  affected symbols/behaviour ... Independently re-verified the code ...
  rather than trusting ... `docs-maintainer`'s own claim"); phase-74
  retro "Lessons learnt" (the hypothesis as stated, and its own "the
  audit worked correctly here despite the risk" concession)
- **classification:** unsupported
- **status:** discarded
- **recurrence:** n/a — one occurrence, evaluated and found unsupported
- **curation (knowledge-curator, 2026-09-27).** **Outcome: discard.**
  One-line reason:
  the audit's own persisted report shows an independent, full-repo,
  exact-string/symbol grep-based search method that explicitly distrusts
  `docs-maintainer`'s claim rather than building on it — this directly
  contradicts the "courtesy list anchored the audit" theory. The real
  explanatory factor for the six misses is `docs-maintainer`'s own
  reconciliation methodology, tracked separately as `L-058`, not the
  dispatch-prompt wording. If a future audit's own report shows a search
  actually restricted to a courtesy list (e.g. a finding scoped only to
  the named files, or the report stating it treated the list as
  sufficient), re-open as a fresh candidate then — this specific
  occurrence provides no such evidence.

### L-058 — `docs-maintainer`'s own current-truth reconciliation pass must grep the full repository for a changed symbol/behaviour's exact name and the specific stale-claim phrasing it invalidates, not rely on directory-scoped review — generalizes `L-055`'s post-fix completeness-grep discipline to a second role and artifact class

- **origin:** `planning/retros/phase-74-provenance-hardening.md` "What
  didn't work" + "Lessons learnt" + "Process-improvement feedback";
  `planning/retros/_drift-audit-phase-74.md`; independent
  knowledge-curator triage
- **date:** 2026-09-27
- **project_revision:** `050e366` (the behavioural change:
  `symbol_enrichment.model`, `ExternalAdapterProcess.initialize`
  ecosystem/capabilities validation); `docs-maintainer`'s own initial
  reconciliation pass (a dispatch between `050e366` and `40e7718`, not
  itself a commit); `40e7718` (follow-on fix: six current-truth locations
  + five `docs/domain/` locations, landed only after
  `docs-reconstructor`'s independent audit)
- **observation:** `docs-maintainer`'s Phase 74 dispatch was scoped, per
  its own fixed agent-definition, to `README.md`, `docs/`,
  `architecture/`, `ai-docs/`, `CONTRIBUTING.md`, and it reported only
  `docs/protocol-adapter/wire-protocol.md` needed updating.
  `docs-reconstructor`'s independent per-phase drift audit
  (`_drift-audit-phase-74.md`) subsequently found six more BLOCKING
  current-truth findings the reconciliation pass missed: `README.md:276-278`,
  `README.md:165-178`, and `README.md:279-282` (three separate locations
  *inside the one document explicitly named in `docs-maintainer`'s own
  dispatch scope*), `architecture/context-graph-schema.md:94-96`,
  `docs/developer/writing-an-adapter.md:153-166`, and
  `docs/protocol-adapter/integrating-a-new-external-adapter.md` (two
  sub-findings). Two of the six misses being in `README.md` itself — a
  document the reconciliation pass was explicitly told to check — rules
  out "wrong directory scope" as the explanation; the actual variable is
  *methodology within the correct scope*. The audit's own "Scope note"
  describes its method precisely: grepping for the exact affected
  symbols/behaviour (`symbol_enrichment`, `record_symbol_enrichment`,
  `initialize(`, `expected_ecosystem`) and the specific superseded-claim
  phrasing (`"not validated"`, `"uncomplainingly"`, `"observed gap"`)
  across the *entire* current-truth surface, and explicitly states it
  did not trust `docs-maintainer`'s own claim. `docs-maintainer`'s own
  report does not describe an equivalent exact-string/symbol grep — the
  retro's own "Process-improvement feedback" section already names the
  right candidate fix: "Consider whether `docs-maintainer`'s own dispatch
  should more explicitly instruct a full-repository grep for every
  changed symbol/behavior name (not just a directory sweep)." This is the
  same underlying shape `L-055` already named for a different role
  (`context-researcher`'s domain-corpus citation-staleness revisions): a
  reconciliation/fix pass declares itself complete having checked the
  specific things it thought to check, and only an independent,
  exhaustively-grepped audit catches the sibling instances left behind.
  Unlike Phase 73's weaker, single, first-attempt-caught instance (see
  `L-057`, which by contrast needed no rework), this miss was **not**
  caught until the independent audit ran — a real, evidenced process gap
  in `docs-maintainer`'s own ordinary reconciliation methodology, not
  merely the audit doing its job as designed.
- **evidence:** `planning/retros/_drift-audit-phase-74.md` Findings 1-6
  and its "Scope note"; phase-74 retro "What didn't work", "Lessons
  learnt", "Process-improvement feedback"; `.claude/agents/docs-maintainer.md`
  current "What to do" step 2 (directory-scoped, no exact-string/symbol
  full-repo grep instruction) and "Hard rules" (no completeness-grep
  requirement analogous to `L-055`'s landed text)
- **classification:** scoped-rule
- **status:** promoted
- **recurrence:** second confirmed instance (after `L-055`/Phase 72) of
  "a reconciliation/fix pass declares completeness on its own
  named-location review; only an independent, full-corpus/full-repo
  grep-based audit catches the sibling instances left behind" — now
  confirmed in a second role (`docs-maintainer`'s ordinary current-truth
  reconciliation, not only `context-researcher`'s domain-corpus
  citation-staleness revision)
- **curation (knowledge-curator, 2026-09-27).** **Outcome: promote.**
  Destination: `.claude/agents/docs-maintainer.md` "Hard
  rules". **Draft addition** (new bullet, alongside the existing `L-037`
  bullet):

  > **Before reporting that a document needs no change, grep the full
  > repository (not just a directory-scoped read) for the exact name of
  > every changed symbol/behaviour and for the specific phrasing that
  > stated the now-superseded claim** (e.g. "not yet fixed," "known gap,"
  > "not validated," "no producer attribution," "uncomplainingly"). A
  > directory-scoped read can miss sibling occurrences even inside a
  > document you were explicitly told to check — confirmed at Phase 74
  > (`L-058`): a reconciliation pass that reported only
  > `wire-protocol.md` needed updating had, in fact, left six BLOCKING
  > current-truth locations false, three of them inside `README.md`
  > itself (a document named in the same dispatch), caught only by
  > `docs-reconstructor`'s independent, grep-based drift audit. This
  > generalizes `L-055`'s "post-fix completeness grep" discipline
  > (originally scoped to `context-researcher`'s domain-corpus
  > citation-staleness revisions) to this role's own ordinary
  > reconciliation pass.

  **Landed by the lead** (`.claude/agents/docs-maintainer.md` "Hard
  rules", following this candidate's own drafted text verbatim), as a
  follow-up amendment since Phase 73/74 were already marked `done`
  (commit `76c441f`) before this triage ran.

### L-057 — an independent `docs-maintainer` reconciliation pass catching a same-phase `src/` completeness gap (a widened matching function's sibling consumer left unmodified) is structurally similar to `L-055` but not yet evidence of a second, distinct rule

- **origin:** `planning/retros/phase-73-doc-relations-filename-matching.md`
  "Scope delivered vs planned" + "What worked" + "Lessons learnt";
  independent knowledge-curator triage
- **date:** 2026-09-27
- **project_revision:** `0f3337d` (core `build_doc_relations_edges`
  filename/stem widening; `relation_enrichment.py::_relation_needle` left
  unmodified for the same widening); `29ced55` (same-phase follow-on fix,
  renamed `_relation_needles`, widened identically)
- **observation:** `docs-maintainer`'s independent reconciliation pass,
  dispatched as part of Phase 73's ordinary review step, found that
  `relation_enrichment.py::_relation_needle` (the excerpt-centering
  helper used during AI enrichment) implemented the same "match a named
  target by title only" logic `build_doc_relations_edges` had just been
  widened to also match by filename/stem — and had not been updated for
  the same widening, meaning a headerless source doc citing a target only
  by filename would still get a worse excerpt. Fixed in the same phase
  (`29ced55`), not deferred. The phase's own retro frames this as
  "matching `L-055`'s own lesson (check every consumer of a widened
  match, not just the primary edge-creation path)". **Independent check
  against `L-055`'s own landed text**, as required:
  `.claude/agents/context-researcher.md` lines 153-164 is explicitly
  scoped to "revising domain-corpus content to close a
  citation-staleness/retired-terminology finding" — a `context-researcher`
  grepping `docs/domain/` prose for remaining literal occurrences of a
  retired term/pattern. This Phase 73 instance is a different role
  (`docs-maintainer`'s ordinary reconciliation, not `context-researcher`
  closing a citation-staleness finding), a different artifact class (a
  `src/` module implementing matching logic, not `docs/domain/` prose),
  and a different mechanism (checking whether a second function
  implementing similar matching logic over the same underlying data was
  updated for a widened rule, not grepping text for a retired string).
  The retro's framing that this "matches `L-055`" is a structural analogy
  (both are "check every sibling instance of an identical pattern before
  considering a change complete"), not the same landed rule applying a
  second time. Also notable, and distinguishing this from `L-058`: unlike
  `L-055`'s own genesis (Phase 72, where an initial fix was declared
  complete and only a *redone, independent* `docs-reconstructor` audit
  later caught the misses, requiring rework) and unlike `L-058` (Phase
  74, where the initial reconciliation pass's miss was likewise only
  caught by the independent audit), this Phase 73 instance was caught by
  the *first* `docs-maintainer` reconciliation pass, in the same phase,
  with no rework needed — the existing process worked as designed on its
  first attempt here, not only after a prior failure.
- **evidence:** `src/codecompass/doc_mapping.py::build_doc_relations_edges`
  (`0f3337d`); `src/codecompass/relation_enrichment.py::_relation_needles`
  (`29ced55`, renamed from `_relation_needle`);
  `.claude/agents/context-researcher.md` lines 153-164 (`L-055`'s actual
  landed scope: domain-corpus citation-staleness revisions); phase-73
  retro "Scope delivered vs planned", "What worked"
- **classification:** uncertain
- **status:** retained
- **recurrence:** first instance of this specific shape (a widened
  `src/` matching function whose sibling consumer over the same data was
  initially unmodified, caught by `docs-maintainer`'s own reconciliation
  pass on its first attempt). Not yet two instances — insufficient to
  generalize a new scoped rule extending `L-055`'s mechanism into
  `docs-maintainer`'s own "Hard rules" or elsewhere in `.claude/agents/`.
- **curation (knowledge-curator, 2026-09-27).** **Outcome: retain**, not
  promote — no promotion yet. This is a real, evidenced, working-as-designed catch — not a
  demonstrated process gap (contrast `L-058`, where the equivalent catch
  *failed* on the first pass this same phase-pair). If a second,
  independent instance occurs (another phase's `src/` behavioral
  widening whose sibling consumer over the same underlying data is left
  unmodified and only caught by reconciliation/audit rather than by the
  implementer's own plan), promote at that point — likely destination
  `.claude/agents/docs-maintainer.md` "Hard rules" (e.g. "when
  reconciling after a phase widens a detection/matching function, grep
  for every other function implementing similar matching against the
  same underlying data") or `CLAUDE.md` §1's existing test-through-real-
  call-site language (`L-021`), whichever the second instance's own shape
  better fits. Not promoting on a single instance.

### L-056 — a `docs-reconstructor` (or any report-writing role) dispatch step in `agent-led-workflow.md` must itself state the report's required persisted file path, not rely on the role's own agent-definition file to guarantee the write happens

- **origin:** `planning/retros/phase-72-stage-c-learnings-and-roadmap-realignment.md`
  "What didn't work" (first bullet) + "Lessons learnt" (third bullet);
  independent knowledge-curator triage of that rework, following up on
  the prior Phase 72 triage pass (`L-051`–`L-054`) which had not yet seen
  this rework's own retro update
- **date:** 2026-09-27
- **project_revision:** f2f7cbf (redone drift-audit report persisted);
  71f5949 (retro/CONTEXT/CHANGELOG closeout of the rework)
- **observation:** Phase 72's first `docs-reconstructor` per-phase
  dispatch produced a real, substantive verbal finding (a "Stage E"
  citation-staleness cluster, correctly routed to `domain-skeptic` and
  fixed in `336b4cd`) but never wrote the standalone report file
  (`planning/retros/_drift-audit-phase-72.md`) required by every phase
  from 45 through 71. This was caught only by `release-phase-auditor`'s
  own independent DoD audit (first pass: FAIL) — not by any step in the
  phase's own execution or by `planning/agent-led-workflow.md` step 9
  itself (the step that dispatches this exact audit). Checked directly:
  `.claude/agents/docs-reconstructor.md` MODE 1's own "Output" section
  *does* state the path ("a short report
  `planning/retros/_drift-audit-phase-NN.md` (or wherever the lead
  says)") — the role's own definition is not silent on this. But
  `agent-led-workflow.md` step 9's own text ("Dispatch `docs-reconstructor`
  in per-phase mode with the phase diff... It reports `NO DRIFT` or a
  list of current-truth doc sentences the change made false") never
  restates the persisted-file requirement at the point a dispatch prompt
  is actually composed — it describes the report's *content*, not that
  the dispatch prompt must explicitly instruct the agent to write it to
  that path. This is the same shape as `L-041` (`context-health-planner`'s
  own charter promised a cadence `agent-led-workflow.md`'s actual step
  never carried) and `L-036`/`L-046` (a role's own stated requirement,
  never re-stated at the point of dispatch, is structurally likely to be
  silently dropped) — a role's own file stating a requirement is not the
  same as that requirement being operationalized into the step sequence
  that actually invokes the role.
- **evidence:** `.claude/agents/docs-reconstructor.md` lines 57-58
  ("**Output** — a short report `planning/retros/_drift-audit-phase-NN.md`
  (or wherever the lead says)"); `planning/agent-led-workflow.md` step 9
  (no restatement of the output path in the dispatch instruction itself);
  `planning/retros/_drift-audit-phase-72.md` line 9 ("the standalone
  report file was never written to disk at the time"); phase-72 retro
  "What didn't work" first bullet
- **classification:** workflow
- **status:** promoted
- **recurrence:** first confirmed instance of this exact failure (a
  report-writing role's verbal finding landing correctly but its
  persisted-file requirement silently dropped); same underlying shape as
  `L-041`/`L-036`/`L-046`'s "stated-but-not-operationalized requirement"
  class, third+ occurrence of that broader class
- **promoted_to:** `planning/agent-led-workflow.md` step 9 (landed by
  the lead, Phase 72 closeout, following this candidate's own drafted
  text)
- **curation (independent post-rework triage, 2026-09-27,
  knowledge-curator):** accept and recommend **promote**. Checked both
  named documents directly, as asked: `docs-reconstructor.md`'s own
  "Output" text already names the path, so this is not a case of the
  role's own definition being silent — but nothing about a role's own
  file being correct guarantees a *lead's dispatch prompt*, composed from
  `agent-led-workflow.md` step 9's own (shorter, content-focused) text,
  actually re-states that path when the prompt is written. That gap —
  between what a role's own brief says and what the workflow step that
  invokes it says — is exactly the shape `L-041` already named and fixed
  for `context-health-planner`'s cadence; this is the same shape applied
  to a different missing operationalization (a required output path
  rather than a required dispatch cadence). **Draft amendment** to
  `planning/agent-led-workflow.md` step 9 (insert after the existing
  first sentence): "State explicitly in the dispatch prompt that its
  report must be written to `planning/retros/_drift-audit-phase-N.md` —
  do not rely on `docs-reconstructor.md`'s own agent-definition file to
  guarantee the write happens. A first dispatch of this exact step at
  Phase 72 produced a substantive verbal finding but no persisted file,
  caught only by `release-phase-auditor`'s independent DoD audit, not by
  any step in this workflow's own sequence (`L-056`)." The lead should
  also consider (not drafted here, since it widens scope beyond the one
  concrete failure) whether the same clause belongs at every other
  report-writing-role dispatch point in this file (step 4
  `context-health-planner`, step 13 `release-phase-auditor`, any
  `domain-skeptic` dispatch) — flagging this as a live question for the
  lead rather than pre-deciding it, since only one concrete failure (this
  one) has actually occurred so far. Not landing the `agent-led-workflow.md`
  edit directly — outside this role's write boundary; drafted here for
  the lead to review and land.

### L-055 — a fix commit closing a drift-audit/domain-skeptic finding needs its own completeness check against every sibling instance of the identical retired-terminology pattern, not just the specific locations the triggering report first named

- **origin:** `planning/retros/phase-72-stage-c-learnings-and-roadmap-realignment.md`
  "What didn't work" (second bullet) + "Lessons learnt" (second bullet);
  `planning/retros/_drift-audit-phase-72.md` §3; independent
  knowledge-curator triage of that rework
- **date:** 2026-09-27
- **project_revision:** 336b4cd (incomplete fix); 5d6a37d (follow-on
  fix for the 3 sibling instances + 1 stale citation)
- **observation:** `336b4cd` correctly fixed the exact four locations
  `domain-skeptic`'s Phase 72 report named (`claim.md`, `decision.md`,
  `relationship-edge.md`, `open-questions.md` item 7) and correctly
  superseded the two originating Claims. The redone `docs-reconstructor`
  drift audit (`_drift-audit-phase-72.md` §3), grepping independently for
  every occurrence of the retired "Stage E"/"Stage C" terminology in
  `docs/domain/` rather than trusting the fix commit's own scope, found
  three sibling instances of the identical pattern the fix left behind —
  `decision.md:27` and `decision.md:101` (two more instances *in the same
  file* `336b4cd` was already editing for this exact issue, one only 62
  lines from the sentence it did fix) and `observation.md:51` (a file the
  fix commit never touched at all, despite sharing the same collision
  material as the files it did touch) — plus a fourth, weaker instance
  (`evidence.md:106`'s stale `CL-EVID-009` citation, not updated to
  `CL-EVID-011` the way `claim.md`'s parallel citation was). **Independent
  check against `L-051`, as asked:** `L-051`'s own landed text
  (`.claude/agents/domain-skeptic.md` step 3) instructs `domain-skeptic`,
  "when running a freshness reconciliation pass specifically," to "grep
  for known fragile term-classes directly... rather than relying solely
  on 'does the triggering diff touch a file/symbol/behaviour this page
  cites.'" That is a **detection-time** instruction — it governs the
  initial search that produces a finding. This candidate's failure
  happened at a different moment: **after** a finding had already been
  named and a fix drafted, nobody (`domain-skeptic`, `context-researcher`,
  the lead) re-grepped the corpus to confirm the fix actually closed
  every occurrence the same search would have found. `L-051`'s text does
  not say "and re-run this grep against the fix's own final state before
  considering the finding closed" — it is silent on fix-completeness
  verification specifically. This is a distinct, narrower moment than
  `L-051` covers, not a re-statement of it — though the retro's own text
  is right that it is "a narrower instance of the same shape" (a retired
  label is fragile wherever it appears, checked or not), the *mechanism*
  that would prevent recurrence (a post-fix completeness grep, owned by
  whoever executes the correction) is not the same mechanism `L-051`
  already installed (a pre-finding detection grep, owned by
  `domain-skeptic` during its own adversarial pass). Note also that
  `L-051` itself postdates the `336b4cd` dispatch chronologically (it was
  promoted *from* analysis of this same phase's events), so even had
  `domain-skeptic`'s original report-writing pass used full-corpus
  grepping throughout, that alone would not establish a standing
  completeness check for whoever *executes* a fix afterward — a separate
  actor, a separate moment, and (per `decisions/0060`'s write-boundary
  split) frequently a separate role (`context-researcher`, not
  `domain-skeptic`, per this same phase's own "What worked" section).
- **evidence:** `planning/retros/_drift-audit-phase-72.md` §3 (the three
  sibling instances + one weaker instance, with file:line); commit
  `336b4cd` (the incomplete fix); commit `5d6a37d` (the follow-on
  completeness fix); `.claude/agents/domain-skeptic.md` step 3 (`L-051`'s
  landed text, scoped to detection during a freshness-reconciliation
  pass, not to post-fix verification)
- **classification:** scoped-rule
- **status:** promoted
- **recurrence:** first confirmed instance of this specific gap
  (post-fix completeness verification against sibling instances); related
  to, but a distinct moment from, `L-048`/`L-051`'s citation-fragility
  class (now four+ occurrences of *that* class)
- **promoted_to:** `.claude/agents/context-researcher.md` "Hard rules"
  (extending the same `L-048`/`L-051` bullet — landed by the lead, Phase
  72 closeout)
- **curation (independent post-rework triage, 2026-09-27,
  knowledge-curator):** accept and recommend **promote**, as a targeted
  amendment to the *same* `L-048`/`L-051` bullet in
  `.claude/agents/context-researcher.md` "Hard rules" (the role that
  actually executes a `docs/domain/` correction per this phase's own
  write-boundary finding), rather than a free-standing new rule or a
  `domain-skeptic.md` change — `domain-skeptic` is read-only toward the
  corpus and does not execute fixes, so a completeness check belongs with
  the role that does the editing. **Draft amendment** (append to the
  existing bullet, after the `L-051` sentence): "When revising
  domain-corpus content to close a citation-staleness/retired-terminology
  finding, grep the full corpus for every remaining occurrence of the
  identical retired term or pattern before considering the revision
  complete — not only the specific locations the triggering report named.
  A fix scoped to only the named locations can leave sibling instances of
  the identical pattern behind, including in files the fix is already
  editing for the same underlying issue: confirmed at Phase 72
  (`336b4cd` fixed exactly the four locations `domain-skeptic`'s report
  named, missing three sibling instances plus one stale citation, two of
  them in a file `336b4cd` was already editing — caught only by a redone,
  independent `docs-reconstructor` audit, `L-055`)." Also recommend the
  lead consider (not drafted here, since it's a broader, unconfirmed
  extension) whether `release-phase-auditor`'s own DoD checklist should
  gain an explicit item verifying a fix commit's completeness against a
  full-corpus grep whenever it closes a named staleness finding — this
  would add an independent backstop rather than relying solely on
  `context-researcher`'s own self-check at fix time, matching this
  project's general preference for independent verification over
  self-certification (`CLAUDE.md` §5). Flagging, not deciding, since only
  one concrete instance has occurred and `release-phase-auditor`'s
  existing general "re-runs verification" mandate arguably already covers
  it in principle. Not landing the `context-researcher.md` edit directly
  — outside this role's write boundary; drafted here for the lead to
  review and land.

### L-054 — `docs-reconstructor`'s domain-claim staleness flag matched on body-text mentions of a retired label across more pages than actually cited it in their own References block — over-inclusive but harmless given `domain-skeptic`'s own follow-up verification

- **origin:** `planning/retros/_domain-skeptic-review-phase-72.md`, "A
  secondary finding: the audit's own framing overstated uniformity"
- **date:** 2026-09-27
- **project_revision:** 336b4cd
- **observation:** Phase 72's per-phase drift audit named seven
  `docs/domain/concepts/*.md` pages plus one `open-questions.md` item as
  domain-claim staleness candidates tied to `roadmap.md:1061-1087`'s
  "Stage E" framing. `domain-skeptic`'s own follow-up check found only
  three of the seven (`evidence.md`, `claim.md`, `decision.md`) actually
  cite that line range verbatim in their own References block;
  `provenance.md` cites a narrower range; `observation.md`,
  `derivation.md`, and `relationship-edge.md` don't cite it in References
  at all, only mentioning "Stage E" in body text — yet all were flagged.
  `development-methodology.md` checkpoint 1's own written criterion for
  this check is "if a phase's diff touches a file, symbol, or behaviour a
  `docs/domain/concepts/*.md` page's own references block cites" —
  narrower than what evidently ran, since Phase 72's diff never touched
  `roadmap.md` (the cited file) at all; the actual staleness came from
  `decisions/0062`, an unrelated file, retiring the framing the citation
  depended on.
- **evidence:** `planning/retros/_domain-skeptic-review-phase-72.md`
  "Precisely which pages are affected" and "A secondary finding" sections;
  `planning/v1-redefinition/development-methodology.md` "Domain-corpus
  freshness and reconciliation" checkpoint 1's literal text
- **classification:** scoped-rule
- **status:** retained
- **recurrence:** first occurrence of this specific over-flagging pattern;
  no downstream harm since `domain-skeptic`'s own verification step
  (already required, per checkpoint 1's "not a finding... only that it is
  worth `domain-skeptic` looking again") caught and correctly narrowed it
  before any fix landed
- **promoted_to:**
- **curation (Phase 72 triage, 2026-09-27, knowledge-curator):** this is
  arguably a feature, not a bug — a cheap, over-inclusive flag with a
  cheap, precise verification step downstream is a reasonable
  recall/precision tradeoff, and `domain-skeptic`'s own report treats it
  as "worth noting... though it doesn't change the substantive verdict,"
  not a defect. Also notable: `docs-reconstructor`'s actual behaviour here
  was broader than checkpoint 1's own literal written criterion (it
  flagged pages whose cited file was never touched by the diff, catching
  a real staleness anyway) — worth someone eventually writing down what
  actually triggered the flag this time, since the documented criterion
  alone would not have predicted this catch. Not promoting a rule change
  from one instance where the audit's looser-than-documented behaviour
  happened to work in the project's favour. **Outcome: retain** — revisit
  if a future instance shows either (a) the same broad matching producing
  a genuinely wasteful false-positive load, or (b) the narrower documented
  criterion actually missing a real case the broader behaviour would have
  caught.

### L-053 — independent fork review, not the lead's own second read, caught a disposition entry's own omission of an existing (relocated) design document — a repeat of `L-049`'s shape, not yet a promotable rule

- **origin:** Phase 72 retro "What worked" (fork-review finding, landed
  `c0c0d15`)
- **date:** 2026-09-27
- **project_revision:** c0c0d15
- **observation:** `planning/pre-v1-disposition.md`'s Phase 24 entry
  originally stated Phase 24 "never had its own numbered plan file"
  without citing `planning/phase-20-chat-project-root-routing-design.md`
  — a real design document for exactly that scope, relocated from
  `architecture/overview.md` at Phase 65 — which does exist. An
  independent fork review caught this; the lead's own second
  read-through of the same disposition table had not. Fixed in `c0c0d15`.
- **evidence:** `planning/pre-v1-disposition.md` §3 (current text, citing
  `planning/phase-20-chat-project-root-routing-design.md`); commit
  `c0c0d15` ("cite Phase 20's own design doc under Phase 24's
  disposition"); `planning/retros/phase-72-stage-c-learnings-and-roadmap-realignment.md`
  "What worked" third bullet
- **classification:** uncertain
- **status:** retained
- **recurrence:** related to `L-049` (Phase 71, a fork review catching a
  line-count discrepancy the lead's own drafting missed) — same shape (an
  independent completeness/consistency check catching what a second
  read-through by the lead alone missed), different concrete content (a
  missing citation to an existing document, vs. an imprecise numeric
  estimate); neither individually promoted, per `L-049`'s own reasoning
  against promoting a rule from a single harmless miss
- **promoted_to:**
- **curation (Phase 72 triage, 2026-09-27, knowledge-curator):** following
  `L-049`'s own precedent exactly — a second instance of "independent
  fork review earns its cost" doesn't yet justify inventing a
  project-rule (e.g. "always grep `planning/phase-N-*` and
  `architecture/overview.md`'s relocation history before writing a
  backlog disposition entry"); the retro's own "What didn't work" section
  already treats this as the review step working as designed, not a
  process failure. **Outcome: retain** — revisit if a third instance of
  this shape (an independent review catching a completeness gap the
  lead's own read missed) recurs with real, not just cosmetic,
  consequence, per `L-049`'s own revisit condition.

### L-052 — confirming that a Claim/Evidence-model correction limited to a resolution-mechanism reference still goes through full Claim-supersedes-Claim, not a lighter edit, matches `development-methodology.md`'s already-unconditional rule — no new rule surfaced

- **origin:** Phase 72 retro "Lessons learnt" (explicitly left to
  `knowledge-curator`'s own independent assessment)
- **date:** 2026-09-27
- **project_revision:** c0c0d15 (`CL-EVID-011`/`CL-EVID-012`'s own
  recorded `repository_revision`)
- **observation:** `context-researcher` superseded `CL-EVID-009`/
  `CL-EVID-003` with `CL-EVID-011`/`CL-EVID-012` for a narrow, mechanical
  correction (retiring "Stage E" as the named future-resolution vehicle)
  — the first time this project's Claim-supersedes-Claim mechanism has
  been exercised with real content (`CL-EVID-012`'s own statement: "the
  first real exercise... a narrow, mechanical resolution-mechanism
  correction, not a substantive reversal"). The retro frames this as a
  possible new process rule. Checked directly:
  `development-methodology.md`'s "Traceability without silent rewriting"
  section already states, unconditionally and with no severity/magnitude
  carve-out, that "Domain and Design artifacts are never edited in place
  once approved. A superseded Claim, Derivation, Decision, or Requirement
  gets a **new** record..." — this rule already covers any correction to
  a Claim, narrow or substantive, with no exception written for
  citation-only/reference-only fixes. Phase 72's use is a clean,
  unsurprising application of an already-fully-general rule, not a
  discovery of a boundary case the rule hadn't already settled.
- **evidence:** `planning/v1-redefinition/development-methodology.md`
  "Traceability without silent rewriting" (the unconditional rule text,
  unchanged since it was written); `planning/knowledge/codecompass-domain/CL-EVID-012.yaml`
  (states plainly this was "a narrow, mechanical resolution-mechanism
  correction, not a substantive reversal" and that the mechanism's
  behaviour "under a genuine contradiction... remains honestly untested"
  — i.e. the domain corpus itself already records the caveat the retro
  raises, durably, without needing a duplicate learnings-queue entry)
- **classification:** uncertain
- **status:** discarded
- **recurrence:** none — first and only instance so far of the mechanism
  firing with real content
- **promoted_to:**
- **curation (Phase 72 triage, 2026-09-27, knowledge-curator):** matches
  the `L-047` precedent exactly (two self-review catches at Phase 71 that
  "confirm existing rules already work, surfacing no new gap" →
  discard). Here too: the rule that decided how to handle this correction
  was already fully general before Phase 72, the correction followed it
  without needing interpretation or exception, and the one genuinely open
  fact this phase surfaces (the mechanism remains untested under a real,
  substantive contradiction) is already recorded, durably, in
  `CL-EVID-012.yaml`'s own text — filing a second, duplicate record of the
  same caveat in the learnings queue would be exactly the low-value
  pile-up the lifecycle's "no giant permanent AI learnings document"
  principle warns against. **Outcome: discard** — reason: confirms an
  already-unconditional rule; the one real open question is already
  durably recorded elsewhere.

### L-051 — a domain-corpus citation naming a live project phase-group/gate label (not just a document's content) as a future-resolution mechanism is exactly as fragile to an unrelated organisational restructure as `L-048`'s document-content citations — a third/fourth instance, now also inside a Claim record and this project's own `context-gaps` queue

- **origin:** Phase 72 retro "What worked" +
  `planning/retros/_domain-skeptic-review-phase-72.md` + this triage's
  own independent check of `planning/context-gaps/inbox.md`
- **date:** 2026-09-27
- **project_revision:** 336b4cd (domain-corpus fix); this triage's own
  session (context-gaps/inbox.md fix, uncommitted at filing time)
- **observation:** `decisions/0062` (Phase 72) retires the "Stage E"
  phase-group label project-wide. `domain-skeptic`'s Phase 72 review
  found this made "Stage E's own future Domain stage" stale inside
  `CL-EVID-009`/`CL-EVID-003` and four `docs/domain/concepts/*.md` pages
  — the third occurrence of the citation-fragility `L-048` already names,
  but the first inside a Claim record rather than a concept page's
  References list, and the first requiring `context-researcher`'s
  Claim-supersession mechanism (not a citation-list edit) to fix.
  Independently, this triage found the identical pattern in
  `planning/context-gaps/inbox.md`'s own `classification:` fields for
  `CG-001`, `CG-003`, `CG-007` ("graph-capability (Stage E / GATE DD)"),
  a location outside both `domain-skeptic`'s Phase 72 scope (`docs/domain/`
  only) and `context-researcher`'s (Claim records only) — a fourth
  instance, self-caught by this curation pass, not by any dedicated
  freshness check, and fixed directly in this same triage (within this
  role's own write boundary, `planning/context-gaps/**`).
- **evidence:** `planning/retros/_domain-skeptic-review-phase-72.md` "The
  staleness originates in a Claim record, not just corpus prose";
  `planning/knowledge/codecompass-domain/CL-EVID-011.yaml`/`CL-EVID-012.yaml`
  (supersession); `planning/context-gaps/inbox.md` `CG-001`/`CG-003`/
  `CG-007` classification fields (fixed in this same triage, Phase 72
  curation notes added to `CG-001`/`CG-003`/`CG-006`/`CG-007`)
- **classification:** scoped-rule
- **status:** promoted
- **recurrence:** third/fourth occurrence of `L-048`'s underlying class
  (Phase 66 `CONTEXT.md` rewrite; Phase 71 `ROADMAP.md` restructure;
  Phase 72's `decisions/0062` Stage-E retirement, twice — once inside a
  Claim, once inside `context-gaps/inbox.md`)
- **promoted_to:** `.claude/agents/context-researcher.md` "Hard rules"
  (extended the `L-048` rule) and `.claude/agents/domain-skeptic.md`
  step 3 (landed by the lead, Phase 72 closeout, following this
  candidate's own drafted text)
- **curation (Phase 72 triage, 2026-09-27, knowledge-curator):** accept
  and recommend **promote** — amend the already-landed `L-048` rule in
  `.claude/agents/context-researcher.md` "Hard rules" to explicitly cover
  "a live project phase-group/stage/gate/priority-track label used as a
  future-resolution-mechanism reference," not only "another document's
  current content," and add a pointer that this fragility class isn't
  confined to `docs/domain/`: it can occur inside a Claim record's own
  statement text (out of this role's write boundary — `context-researcher`'s
  territory) and inside this project's own `context-gaps/inbox.md`
  classification fields (fixed directly in this triage). Also recommend
  `.claude/agents/domain-skeptic.md`'s own contradiction-search step
  (already amended once for within-page consistency, `L-033`) gain a note
  to grep for "Stage E" / other retired phase-group names as a known
  fragile term-class during a freshness reconciliation pass, rather than
  relying solely on the diff-touched-file heuristic
  (`development-methodology.md` checkpoint 1's literal criterion — "diff
  touches a file/symbol/behaviour the page's own references cite" — did
  not, on its own written text, predict this catch, since Phase 72's diff
  never touched `roadmap.md` itself; see `L-054` for the related
  over-flagging finding). Not landing either `.claude/agents/*.md` edit
  directly — outside this role's write boundary; drafted here for the
  lead to review and land.

### L-050 — `CLAUDE.md` §2's own description of `planning/ROADMAP.md` ("full-roadmap phase-status table (all phases, not just the current one)") is now stale against Phase 71's approved restructure

- **origin:** independent read for the Phase 71 `knowledge-curator`
  triage, following up on `planning/retros/_drift-audit-phase-71.md` §3's
  second bullet (flagged there as a "possible tension between Phase 71's
  restructure and `CLAUDE.md` §2's own standing requirement," explicitly
  left unresolved by that audit: "not something I can resolve or that a
  docs fix alone settles")
- **date:** 2026-09-25
- **project_revision:** 40fc074
- **observation:** `CLAUDE.md` §2 states `planning/ROADMAP.md` is a
  "full-roadmap phase-status table (all phases, not just the current
  one)." Phase 71's approved restructure (`4bc7c1d`) replaced
  `ROADMAP.md`'s 424-line phase-by-phase table with a ~113-line
  current-state summary; `ROADMAP.md`'s own new header states explicitly
  that full phase-by-phase history is "preserved in three places, not
  repeated here as a 70-row table." `CONTRIBUTING.md` and
  `ai-docs/CLAUDE.md`'s own descriptions of `ROADMAP.md` were already
  corrected to match this reality in `396118a` (the drift-audit-findings
  commit) — but `CLAUDE.md` §2 itself, the one document §0 says every
  session "trusts unconditionally on load," was not touched, and cannot
  be touched by any agent without an explicit user-approved diff (§0).
  This is a real, currently-live inaccuracy in `CLAUDE.md`'s own text,
  not merely in a downstream doc that mirrors it — and the retro's own
  "Candidate learnings filed" section does not mention it at all.
- **evidence:** `CLAUDE.md` §2 (current text, unchanged since before
  Phase 71); `planning/ROADMAP.md` lines 1-21 (current header, "not
  repeated here as a 70-row table"); `CONTRIBUTING.md`:56-58 and
  `ai-docs/CLAUDE.md`:21-25 (both already corrected in `396118a` to
  describe `ROADMAP.md` as "v1.0.0's own shipped status, deferred items
  with revisit triggers, and post-v1 development tracking" rather than a
  full phase table); `planning/retros/_drift-audit-phase-71.md` §3 (names
  the tension, explicitly declines to resolve it, calls the equivalent
  `CONTRIBUTING.md` wording "Blocking"); `planning/v1-redefinition/proposed-governance-changes.md`
  checked directly end to end — sections A-D, none address this bullet.
- **classification:** project-rule
- **status:** promoted
- **recurrence:**
- **promoted_to:** `CLAUDE.md` §2's `planning/ROADMAP.md` bullet
  (landed by the lead, Phase 71 closeout, after explicit user approval
  per §0, following this candidate's own drafted diff verbatim —
  `planning/v1-redefinition/proposed-governance-changes.md` §E)
- **curation (Phase 71 triage, 2026-09-25, knowledge-curator):**
  accepted and independently re-verified — read `CLAUDE.md` §2,
  `ROADMAP.md`'s current header, `CONTRIBUTING.md`, and `ai-docs/CLAUDE.md`
  directly rather than taking the drift audit's account on faith; all
  confirmed. None of this phase's five commits
  (`657dceb`/`4bc7c1d`/`0e36123`/`396118a`/`40fc074`) touches `CLAUDE.md`
  (expected — §0 requires explicit user approval first), so this
  genuinely fell through: the drift audit found it and correctly declined
  to resolve it itself (out of scope for that role), and the retro's own
  closeout never picked it back up as a follow-on action item. **Outcome:
  promote (recommendation + draft only).** `CLAUDE.md` is never written
  directly by this agent or any agent (§0, this agent's own hard rules) —
  drafted as a new §E in `planning/v1-redefinition/proposed-governance-changes.md`
  for the lead to present to the user as a diff, per that file's own
  established pattern (§D). Not a duplicate of any existing candidate —
  checked `L-034`/`L-013` (both about `ROADMAP.md`/`CONTEXT.md`/plan-file
  Status *line* disagreement across files, a different shape from
  `CLAUDE.md`'s own descriptive prose about what `ROADMAP.md` *is*).

### L-049 — a phase plan's own approximate line-count claim (412) differed from the real pre-restructure count (424), caught only by independent fork review

- **origin:** Phase 71 retro "What didn't work"
- **date:** 2026-09-25
- **project_revision:** 40fc074
- **observation:** `planning/phase-71-post-v1-documentation-refresh.md`
  §1.2 estimated `ROADMAP.md`'s pre-restructure row-table size at 412
  lines; the real count, confirmed via `git show 4bc7c1d~1 | wc -l`, was
  424. Caught by the independent fork consistency review, not by the
  lead's own drafting or by the (also independent) `docs-reconstructor`
  drift audit. No downstream consequence: the number was used only in
  `CONTEXT.md`'s own prose describing the restructure's size, never in a
  gate, threshold, or test.
- **evidence:** `planning/retros/phase-71-post-v1-documentation-refresh.md`
  "What didn't work"; `git show 4bc7c1d~1 | wc -l` → 424 (per the retro's
  own account, not independently re-run here — no Bash available to this
  role).
- **classification:** uncertain
- **status:** retained
- **recurrence:** related to `L-007` (Phase 43c, retained) — a weaker,
  narrower instance of the same broad parent fragility ("a plan's own
  estimate can be imprecise"), but a distinct shape (an approximate
  figure carried into prose without re-verifying against a live command,
  vs. `L-007`'s "mechanism exists vs. mechanism has produced output this
  phase" conflation)
- **promoted_to:**
- **curation (Phase 71 triage, 2026-09-25, knowledge-curator):**
  accepted. Not merging into `L-007` — different enough in shape that
  folding them would blur what each is actually about — but recording
  the relationship so a future third occurrence of either shape counts as
  real evidence toward a shared "verify a plan-stated figure/claim
  against a live check before finalizing" rule, rather than two isolated
  one-offs. This single instance had zero real consequence and was caught
  by exactly the review step this project already runs before every
  commit (independent fork review) — promoting a project-rule ("always
  run `wc -l` before stating a count") from one harmless miss would be
  premature and adds exactly the kind of low-value rule this project's
  own "no giant permanent AI learnings document" principle warns against.
  **Outcome: retain.** Revisit at the next bulk learnings review (note:
  `planning/v1-redefinition/learning-lifecycle.md` §2 only names
  milestone-group bulk-review checkpoints, Phase 47 and Phase 69, both
  now closed — no post-v1 bulk-review cadence is currently scheduled;
  flagging that scheduling gap is `roadmap-context-curator`'s/the lead's
  call, not resolved here) or immediately on a second occurrence where an
  unverified number has real consequence, whichever comes first.

### L-048 — `docs/domain/` illustrative citations of fast-moving planning documents/tests are a recurring fragility class, now confirmed at two independent phases

- **origin:** Phase 71 drift audit (`planning/retros/_drift-audit-phase-71.md`
  §5) + domain-freshness reconciliation
  (`planning/retros/_domain-freshness-reconciliation-phase-71.md`,
  `EV-SKEP-004`); prior occurrence at Phase 66
  (`EV-SKEP-003`/`OBS-SKEP-004`)
- **date:** 2026-09-25
- **project_revision:** 396118a (drift audit) / 40fc074 (fix landed)
- **observation:** `docs/domain/concepts/connector.md`'s Definition
  section cites a fixed list of planning documents as all "currently"
  listing "connector" as a research-candidate term. This list already
  had to be trimmed once, at Phase 66, when `planning/CONTEXT.md`'s
  rewrite dropped its own listing (`EV-SKEP-003`). Phase 71's unrelated
  `ROADMAP.md` restructure broke the same citation list a second time,
  for a different file in the same list (`planning/ROADMAP.md` no longer
  mentions "connector" anywhere after its 424→113-line restructure).
  Both breaks were caused by a planning-document restructure with zero
  change to domain meaning, and both were only caught after the fact by
  a dedicated freshness-reconciliation pass, not prevented at authoring
  time. `docs/domain/concepts/invariant.md`'s "Example" section shows a
  related but distinct fragility in the same corpus: it cites a specific
  test method name
  (`TestReadmePhaseCount::test_ignores_done_phases_in_redefined_v1_section`)
  as `L-001`'s landed proof; Phase 71 deleted that exact test as part of
  the same `ROADMAP.md`-driven `check_readme_phase_count` rewrite,
  leaving the citation dangling even though the underlying promoted-
  learning fact it illustrates (`L-001`, a real promotion) is still true.
- **evidence:** `EV-SKEP-004`/`OBS-SKEP-005`
  (`planning/knowledge/codecompass-domain/`) — direct `grep`/`git show`
  confirmation of the first case; `EV-SKEP-005`/`OBS-SKEP-006` — direct
  `grep`/`git show` confirmation of the second; `EV-SKEP-004`'s own text:
  "this is the second time this exact citation list has gone stale from
  an unrelated planning-document restructure ... worth naming to
  `context-researcher` as a candidate for a more durable citation form."
- **classification:** scoped-rule
- **status:** promoted
- **recurrence:** second independent occurrence (Phase 66 `CONTEXT.md`
  rewrite; Phase 71 `ROADMAP.md` restructure) — same citation-list
  fragility, two unrelated triggering documents
- **promoted_to:** `.claude/agents/context-researcher.md` "Hard rules"
  (landed by the lead, Phase 71 closeout, following this candidate's
  own drafted text verbatim)
- **curation (Phase 71 triage, 2026-09-25, knowledge-curator):** accepted
  — both underlying facts independently re-traced to the cited evidence
  files, not taken on the retro/report's word alone (spot-checked
  `EV-SKEP-004`'s claim that `planning/ROADMAP.md` no longer contains
  "connector" against the current file's own header/body read earlier in
  this same triage — consistent). **Correcting the retro's own framing**:
  the retro's "What worked" section attributes this catch to "the
  domain-corpus freshness-reconciliation mechanism (`L-040`)" — on direct
  inspection this is imprecise. `L-040`'s own promoted checkpoint
  (`development-methodology.md` "Domain-corpus freshness and
  reconciliation" checkpoint 4, "final closeout re-check") is a distinct,
  narrower mechanism for staleness *reintroduced by a phase's own final
  status-bump commit*, confirmed exactly once so far (Phase 66's own
  `CONTEXT.md` filename mention, its origin case) — nothing in either
  supporting report for Phase 71 shows checkpoint 4 running a second time
  (Phase 71's `release-phase-auditor` final DoD pass, which would
  exercise it, is still pending as of this triage). What actually caught
  both Phase 71 cases is the older, pre-`L-040` checkpoint 1 (a per-phase
  drift-audit flag escalated to `domain-skeptic` mid-phase, established
  at Phase 63D) — the same checkpoint that caught the original Phase 66
  `connector.md`/`CONTEXT.md` case. That mechanism is genuinely confirmed
  working twice; `L-040` specifically is not (yet) confirmed twice. This
  distinction doesn't reduce this candidate's own promotability — if
  anything it sharpens it: **this is about prevention, not detection.**
  `docs/domain/`'s own authoring convention for illustrative citation
  lists currently has no guidance steering it away from citing fast-
  moving, actively-restructured planning documents by present-tense
  content ("currently lists X"), when a citation form that survives
  restructuring is available (pin to the git revision the corpus item was
  approved at, or phrase the citation as inherently historical). Two
  independent occurrences across two independent, unrelated
  planning-document restructures meet this project's own recurrence bar
  for promoting directly (matching `L-036`'s precedent: a drift pattern
  confirmed twice is enough, no need to wait for a third). **Outcome:
  promote (recommendation + draft; not landed — `.claude/agents/*.md` is
  outside this agent's write boundary).**

  **Recommended addition — `.claude/agents/context-researcher.md`, "Hard
  rules"** (draft, for the lead to review and land):

  > When drafting or revising a `docs/domain/` page's illustrative
  > citation of *other* project documents (e.g. "these N planning
  > documents all list term X as Y"), do not cite present-tense content
  > of a document this project's own process actively restructures
  > post-v1 (`planning/ROADMAP.md`, `planning/CONTEXT.md`, and any
  > mechanical-check test file tied to CLI/doc structure) without a
  > citation form that survives restructuring — pin to the specific git
  > revision/commit the corpus item was approved at, or phrase the
  > citation as historical ("as of `<SHA>`, ..."), rather than asserting
  > the document's current content. Confirmed twice: Phase 66
  > (`planning/CONTEXT.md` rewrite, `EV-SKEP-003`) and Phase 71
  > (`planning/ROADMAP.md` restructure, `EV-SKEP-004`) each independently
  > broke the same citation list in `docs/domain/concepts/connector.md`
  > this way.

  Also flag, as supporting evidence for the same underlying fragility
  rather than a separate rule: `invariant.md`'s "Example" section citing
  a specific test method name as a promoted learning's proof has the
  identical shape (anchoring to a refactorable implementation detail
  rather than a stable identifier) — `promoted.md`'s own append-only
  `L-NNN` line is already the stable anchor available; citing it as the
  primary reference, with the current regression-test location as a
  secondary, refresh-on-drift detail, would have survived Phase 71's
  rewrite of `check_readme_phase_count`. Not drafting this second half as
  its own rule text — `EV-SKEP-005` already names this as
  `context-researcher`'s own next concrete step (choosing between
  reframing `L-001` as historical or re-pointing to a currently-live
  example); the `.claude/agents/context-researcher.md` addition above
  should be read to cover both citation shapes if the lead adopts it.

### L-047 — two self-review catches during README.md drafting (fabricated URL, overstated provenance) confirm existing rules already work, surfacing no new gap

- **origin:** Phase 71 retro "What worked" (README.md drafting,
  self-review before commit)
- **date:** 2026-09-25
- **project_revision:** 40fc074
- **observation:** A first `README.md` draft fabricated Ledgerkit's repo
  URL (guessed `github.com/simonmichael/hledger` instead of checking
  `planning/reference-projects/ledgerkit/*.md` for the real
  `github.com/ctosullivan/ledgerkit`); a second draft overstated
  `symbol_enrichment`'s own provenance ("every enriched row records which
  model...") when that table's missing producer-attribution column is a
  known, disclosed gap (`L-031`). Both caught by the lead's own
  re-read/grep before committing, not by a separate independent agent.
- **evidence:** `planning/retros/phase-71-post-v1-documentation-refresh.md`
  "What worked" bullet 1; the committed `README.md` (`4bc7c1d`) correctly
  cites `github.com/ctosullivan/ledgerkit` and correctly describes
  `symbol_enrichment` as lacking a producer-attribution column, matching
  `L-031`/`planning/ROADMAP.md`'s Future-improvement backlog.
- **classification:** uncertain
- **status:** discarded
- **recurrence:**
- **promoted_to:**
- **curation (Phase 71 triage, 2026-09-25, knowledge-curator):** both
  catches are instances of already-standing rules doing their job — "do
  not fabricate a URL, verify against the project's own recorded
  evidence" (already named by the retro itself, matching the spirit of
  the already-promoted `L-009`, "fetch externally-authoritative text from
  its own canonical source rather than memory/a template") and "do not
  overstate provenance beyond a disclosed gap" (`L-031` is already on the
  record as a named gap — the second draft's error was failing to
  cross-check against a gap this project's own backlog already names,
  not the discovery of a new fragility class). No new artifact is
  needed: there is no evidence this recurs across drafting tasks
  generally (first and only occurrence of each), the review step that
  caught both is not new, and inventing a project-rule from two catches
  in one drafting session would be exactly the low-value rule-pile-up
  the lifecycle doc's "no giant permanent AI learnings document"
  principle warns against. **Outcome: discard** — reason: confirms
  existing rules/process already work; no gap surfaced.

### L-046 — a credential-passing mechanism proposed to the user should be verified to actually bridge the user's own interactive shell into the agent's own tool environment before the user is asked to use it for a real secret

- **origin:** Phase 70 retro ("What worked", "What didn't work", "Lessons
  learnt", `planning/retros/phase-70-release-v1.md`) — the retro names
  this lesson explicitly and states it is "left for `knowledge-curator`'s
  own independent triage rather than the lead filing it unilaterally, per
  this project's now-standard practice," distinct from (but matching the
  spirit of) `L-034`/`L-038`/`L-039`/`L-041`'s pattern of a retro
  surfacing something the curator, not the lead, actually files.
- **date:** 2026-09-24
- **project_revision:** `4c09185`
- **observation:** During Phase 70's real PyPI publish, neither shell
  environment variables nor a `~/.pypirc` file, both set from the user's
  own interactive `!` shell, bridged into this agent's own tool-call
  environment — confirmed by the retro's own "What worked" account: "the
  actual upload was handed to the user's own shell where credentials
  already worked — the token never needed to enter this agent's own
  context at all." Before that isolation constraint was understood, the
  user was asked to `export` the real PyPI token so the agent's own
  subsequent tool calls could use it; a malformed `export` command (a
  stray space) caused the actual secret value to be typed directly into
  the visible conversation transcript once. No misuse occurred and the
  token was rotated as a precaution (the retro's own "What didn't work"),
  but the retro's own "Lessons learnt" names a cheap check that would
  have caught the isolation first: "a quick, harmless check (e.g. `echo
  $SOME_TEST_VAR` after asking the user to export it) would have caught
  the isolation immediately, before any real credential was typed into
  the visible conversation."
- **evidence:** `planning/retros/phase-70-release-v1.md` lines 54-63
  ("What worked" — the isolation constraint and the correct final
  posture, handing the real upload to the user's own shell), lines 85-92
  ("What didn't work" — the actual near-miss incident), lines 94-103
  ("Lessons learnt" — the proposed harmless-probe check), read in full.
  Searched `planning/learnings/inbox.md` and `planning/learnings/promoted.md`
  for "credential", "secret", "token", "isolation", ".pypirc", and "shell
  environment" — no existing candidate or promotion covers
  credential-passing / shell-to-tool-environment isolation; not a
  duplicate.
- **classification:** workflow
- **status:** promoted
- **recurrence:**
- **promoted_to:** `planning/agent-led-workflow.md` step 6 (verify a
  credential-passing mechanism bridges the user's shell into the
  agent's tool environment via a harmless probe, before requesting a
  real secret)
- **curation (this triage, 2026-09-24, knowledge-curator):** provenance
  accepted — assigned this id, all required fields present, evidenced
  directly from the retro text (not merely trusting the retro's own
  characterisation of itself). Independently assessed whether this is
  genuinely learning-shaped or a one-off, low-severity incident not worth
  a durable rule, as the dispatch instruction asked: **it is
  learning-shaped.** The retro's own account confirms no actual harm
  occurred (precautionary rotation only), but the *recurrence risk* is
  real and structural, not incident-specific — any future phase that
  needs the user to supply a credential via an interactive shell for this
  agent's own subsequent tool use (a future publish, a deploy key, any
  API token) faces the identical bridging ambiguity between "the user's
  shell" and "this agent's tool environment," and the fix costs one
  harmless probe command before the real secret is ever requested. This
  is the same shape as `L-038` (a cheap, mechanical check inserted before
  a specific class of action, to catch an environment mismatch before it
  causes real damage) — not a coincidence; both are "verify an
  environment assumption holds before trusting it with something that
  matters" rules. Checked for a duplicate/merge candidate first (see
  evidence above): none found. **Outcome: promote.** Classification
  `workflow` maps to `planning/agent-led-workflow.md`, matching this
  project's own established practice (every prior `workflow`-classified
  promotion in `promoted.md` landed there, not a `.claude/skills/` entry
  per the lifecycle doc's literal table — precedent overrides the literal
  table here exactly as it did for `L-002`/`L-006`/`L-034`/`L-038`/`L-039`/`L-041`).
  Finalised by the lead — not landed here, outside this role's write
  boundary for that file (`.claude/agents/knowledge-curator.md` "Hard
  rules"). Status left as `candidate` until the lead actually applies the
  amendment below and a `promoted.md` line is added, per
  `learning-lifecycle.md` §4/§6. This is **not** a `CLAUDE.md` candidate:
  it is a per-session operational step (how the lead sequences a
  credential request), not a project-wide rule of the kind §0 protects,
  and `planning/agent-led-workflow.md` is not subject to §0's
  user-approval gate — matching the destination the dispatch instruction
  itself flagged as plausible while correctly noting the *other* named
  option (`CLAUDE.md`) would need that gate if chosen instead.

  **Recommended amendment — `planning/agent-led-workflow.md` step 6**
  (draft, for the lead to review and land; not applied here — insert as a
  new bullet immediately after the existing "The lead implements
  directly, or dispatches one `general-purpose` implementer subagent..."
  text):

  > **Before asking the user to type, `export`, or otherwise enter a real
  > credential or secret via an interactive `!` shell command for this
  > agent's own subsequent tool use, verify with a harmless probe that
  > the proposed mechanism actually bridges the user's shell into this
  > agent's own tool environment** — e.g. ask the user to `export` an
  > innocuous test value first and confirm this agent's own tool calls
  > can see it (`echo $SOME_TEST_VAR`), *before* requesting the real
  > secret. Neither shell environment variables nor a config file (e.g.
  > `~/.pypirc`) written from the user's interactive shell are guaranteed
  > to bridge into this agent's own tool-call environment, and discovering
  > that only *after* asking for the real value risks the value being
  > typed directly into the visible conversation transcript. Confirmed at
  > Phase 70 (`L-046`): a malformed `export` command exposed a real PyPI
  > token in the transcript once, before the isolation was understood; no
  > misuse occurred (the token was rotated as a precaution) but the probe
  > above would have caught the isolation harmlessly first. If the probe
  > shows no bridge exists, do not ask for the real secret at all — hand
  > the credential-requiring action itself to the user's own shell instead
  > (the token/secret never needs to enter this agent's own context), the
  > posture Phase 70 ultimately used correctly.

  Revisit toward a mechanical check only if this prose step proves
  insufficient at a future phase that needs a similar credential.

### L-045 — a learning candidate's own self-imposed "force a decision by Phase N" revisit clause is not checked against the actual current phase by any process step, including the two bulk reviews the lifecycle doc itself names

- **origin:** Phase 69 (milestone closeout; retro "What didn't work" /
  "Lessons learnt", `planning/retros/phase-69-milestone-closeout.md`;
  also recorded as `planning/v1-closeout.md` §6 item 3; filed here on
  `knowledge-curator`'s own independent triage, per the retro's explicit
  deferral of this exact question to this queue rather than the lead
  filing it unilaterally)
- **date:** 2026-09-24
- **project_revision:** 67e4f36 (+ Phase 69 commits)
- **observation:** `L-003`'s own text (added at its Phase 43b curation
  note) committed to a specific forcing point: "If still unresolved at
  the Phase 47 bulk review, force a promote/discard." `planning/v1-redefinition/learning-lifecycle.md`
  §2 independently names Phase 47 and Phase 55 as the queue's own
  standing bulk-review checkpoints — this was not a cadence invented
  by L-003, it already existed in the lifecycle doc's own text. Despite
  that, no bulk learnings-queue disposition actually ran at Phase 47
  (`planning/phase-69-milestone-closeout.md`'s own note: "Phase 47 was
  pure Ledgerkit-findings synthesis, no learnings-queue bulk disposition
  ran") — nothing in Phase 47's own plan file listed the bulk review as
  a scope item, so nothing forced it to happen even though the
  cadence was named, in writing, in a governing doc. The miss then went
  uncaught for a further 21 phases (Phase 48 through Phase 68), across
  every one of those phases' own step-10/step-12 per-phase triage passes,
  until Phase 69's dedicated milestone-scale bulk retro review happened
  to re-read the whole queue end to end. This is a distinct failure mode
  from `L-043` (a candidate's `status:` field silently disagreeing with
  its own already-written curation-note verdict, undetected for ~57
  phases) — `L-003`'s `status:` field was internally consistent
  (`retained`, matching its own curation notes) throughout; the gap here
  is that nothing ever compared the *phase number a candidate's own text
  names as a forcing point* against the *actual current phase number*,
  even at the two checkpoints (Phase 47, Phase 55) explicitly designated
  for exactly that kind of review.
- **evidence:** `planning/learnings/inbox.md`'s own `L-003` entry —
  the Phase 43b curation note's "moves forward when" clause ("If still
  unresolved at the Phase 47 bulk review, force a promote/discard");
  the entry's `status:` staying `retained` unchanged from Phase 43b
  (2026-09-11) through Phase 68 with no curation note added at Phase 47
  or Phase 55; `planning/v1-redefinition/learning-lifecycle.md` §2 ("at
  each phase's step 10, and in bulk at Phases 47 and 55, the curator
  reviews the queue"); `planning/retros/phase-69-milestone-closeout.md`'s
  own "What didn't work" section and its Phase 69 curation note on
  `L-003` itself (this same file, lines ~4340-4372).
- **classification:** workflow
- **status:** promoted
- **recurrence:** first occurrence of this specific gap (a candidate's
  own named forcing-phase going unchecked) — related to, but distinct
  from, the general "a cadence existed somewhere but was never
  operationalized into the actual step sequence" pattern already named
  nine times over in `v1-closeout.md` §6 item 1 (`L-006`, `L-013`,
  `L-018`, `L-023`, `L-034`, `L-036`, `L-038`, `L-039`, `L-041`). Not
  merged into that cluster: item 1's own post-v1 implication is scoped
  to checking a *newly added* role/rule's cadence against the step
  sequence at the moment it's added; it does not cover an
  *already-established* cadence (the Phase 47/55 bulk review, named in
  `learning-lifecycle.md` §2 since Phase 41) simply not being executed
  when its own named phase arrives. That gap needs its own fix, not
  coverage-by-analogy from item 1's already-drafted remedy.
- **curation (Phase 69 triage, 2026-09-24, knowledge-curator):**
  accepted as a candidate and triaged in the same pass, per this
  project's established precedent for well-evidenced first-occurrence
  `workflow` promotions not requiring a second recurrence before
  promotion (`L-006`, `L-018`, `L-023`, `L-043` all promoted on a single
  well-evidenced instance). This is genuinely learning-shaped, not
  adequately captured by having been named once in `v1-closeout.md`'s
  own prose: that document is a one-time milestone-closeout artifact,
  not a durable process rule, and its own item 3 explicitly declines to
  prescribe a fix ("should be tracked as an actual checklist item," with
  no artifact naming *which* checklist or *whose* responsibility it is)
  — leaving it there would repeat the exact failure mode this candidate
  describes: a real observation living only in prose nothing else is
  ever obligated to re-read. **Outcome: promote-recommendation —
  landed by the lead** (`planning/v1-redefinition/learning-lifecycle.md`
  §2, commit `d98963c`); at the time this note was originally written,
  no artifact had landed yet — the curator has no write
  access to `planning/v1-redefinition/learning-lifecycle.md` or
  `planning/agent-led-workflow.md`). Recommended fix, matching this
  project's own established preference (per the nine-instance cluster
  above) for operationalizing a cadence into the actual step sequence
  rather than relying on a fragile free-text-parsing mechanical check:
  1. **Primary fix — `planning/v1-redefinition/learning-lifecycle.md`
     §2 amendment:** add an explicit rule that any curation note
     committing to a numbered forcing point ("if still unresolved at
     the Phase N bulk review/[triage], force a promote/discard") must,
     in the same edit, also be mirrored as a concrete line in Phase N's
     own `planning/phase-N-*.md` plan file once that file exists (or,
     if Phase N's plan doesn't exist yet, added to a short running
     "forcing points due" list this section maintains) — so the
     commitment is checkable from the destination phase's own scope
     list (`CLAUDE.md` §1), not only readable by someone who happens to
     open `inbox.md` and notice the phase number has arrived.
  2. **Secondary fix — same section:** state explicitly that the
     Phase 47/55-style standing bulk-review cadence is itself a
     `planning/phase-N-*.md` scope item for whichever phase lands on
     that number, not an obligation floating free of any specific
     phase's own plan — closing the exact gap that let Phase 47 pass
     with no bulk review and no one noticing until Phase 69.
  3. Both are `planning/v1-redefinition/learning-lifecycle.md` edits —
     outside this agent's write boundary (`planning/learnings/**`,
     `planning/context-gaps/**`, `planning/context-observations/**`,
     `planning/knowledge/**`, draft files under `planning/` only).
     Lead finalises, per this classification's own destination table
     entry (`workflow` → workflow-doc amendment, lead finalises).
- **promoted_to:** `planning/v1-redefinition/learning-lifecycle.md` §2
  (a numbered forcing point must be mirrored into its own destination
  phase's plan file; a standing bulk-review cadence is itself a scope
  item of whichever phase lands on that number)

---

### L-044 — a milestone-level DoD audit needs its own explicit "spot-check enough vs. re-derive from scratch" scope statement named in the plan before dispatch, not left to the auditor's own improvised judgment call

- **origin:** Phase 68 (`release-phase-auditor`'s milestone-level DoD
  audit; retro "What worked" bullet 1 and "Lessons learnt")
- **date:** 2026-09-24
- **project_revision:** ca0bbab (current HEAD at triage time)
- **observation:** Phase 68 was this project's first genuinely
  *milestone-level* audit (a spot-check across every Stage A-G phase's
  own exit criteria, Phases 41-67, plus
  `planning/milestone-closeout-checklist.md` steps 1-7) rather than a
  per-phase re-verification. Its own plan file
  (`planning/phase-68-independent-release-audit.md` §0/§2) named, in
  advance and explicitly, what counted as "spot-check enough" (a
  representative sample: one phase per stage, plus recently-audited
  phases) versus what needed independent re-derivation (the
  checklist's seven steps, each re-run directly). The retro credits
  this explicit scope statement as the reason the audit stayed
  proportionate — real evidence gathered, nothing re-derived that an
  earlier phase's own audit had already settled — and states the
  general lesson: "a milestone-level audit is a genuinely different
  exercise from a per-phase one — it needs its own explicit scope
  statement... named in the plan *before* dispatch, not left to the
  auditor's own improvised judgment call on the day." This is a
  specific instance of a more general principle (`CLAUDE.md` §1
  already requires a plan describing scope for *any* phase) applied to
  a phase-shape this project hadn't produced before, and the retro
  itself frames it as "worth keeping as the template for any future
  milestone-scale audit this project runs" — language that reaches for
  a durable artifact, not just this one plan file as an implicit
  precedent.
- **evidence:** `planning/phase-68-independent-release-audit.md` §0
  ("This is a milestone-level audit, not 68 individual per-phase
  re-audits from scratch...") and §2 (the explicit per-item spot-check
  vs. re-derive breakdown); `planning/retros/phase-68-independent-release-audit.md`
  "What worked" bullet 1 and "Lessons learnt"; `planning/retros/_audit-phase-68.md`
  §2.1 item 3 (the auditor's own report explicitly following the
  plan's spot-check sample, not re-deriving all 27 phases). Checked
  `planning/agent-led-workflow.md` and `.claude/agents/release-phase-auditor.md`
  directly (2026-09-24): neither currently distinguishes a
  milestone-level dispatch's scoping needs from a per-phase one — the
  distinction exists only in this one phase's plan file today.
- **classification:** workflow
- **status:** retained
- **recurrence:** first occurrence (this is the first milestone-level,
  as opposed to per-phase, `release-phase-auditor` dispatch this
  project has run)
- **curation (Phase 68 triage, 2026-09-24, knowledge-curator):**
  provenance accepted — the plan file, both retro sections, and the
  audit report were independently re-read (not taken on the retro's
  own characterization alone), and the plan's §0/§2 do contain the
  explicit scope statement the retro credits. Assessed independently
  whether this is adequately captured by the plan file's own existence
  as an implicit template versus being genuinely un-filed and
  learning-shaped: it is real and specific enough to file (a concrete,
  reusable practice, not a restatement of `CLAUDE.md` §1's general
  planning requirement — the general requirement is "describe scope";
  this is the sharper, milestone-specific corollary "for a
  spot-check-shaped audit, scope means naming what counts as sampled
  vs. re-derived, in advance"), but it is **single-occurrence** — this
  is the first milestone-level audit this project has run, so there is
  no second data point yet confirming the pattern generalizes rather
  than being incidental to this one phase's own care. **Outcome:
  retain, not promote yet** — matching this project's own established
  bar for `workflow`-classified candidates (contrast `L-035`, promoted
  only once a second, differently-shaped instance confirmed the
  pattern). Plausible destination, once/if it recurs: a short paragraph
  in `.claude/agents/release-phase-auditor.md` and/or
  `planning/agent-led-workflow.md` naming that a milestone-level (as
  opposed to per-phase) dispatch's own plan must state its spot-check
  scope explicitly before dispatch. Revisit at the next milestone-scale
  audit this project runs (plausibly a future post-v1.0.0 milestone
  group, since Phase 69/70 close out the current one without another
  milestone-level DoD sweep) — if that phase's plan also states this
  discipline explicitly (whether because someone remembered, or because
  this candidate was consulted), that is recurrence-2 and promotion
  should follow: if it's omitted and something is missed as a result,
  that is a stronger, harder form of the same case.
- **promoted_to:** — (not yet; retained)

### L-043 — no mechanical check cross-references a learning candidate's own `status:` field against the verdict its own curation note records, except for the `promoted` case

- **origin:** Phase 68 (`release-phase-auditor`'s milestone-level DoD
  audit, `planning/retros/_audit-phase-68.md` §5 "Non-blocking
  observation"; `knowledge-curator` triage of that finding)
- **date:** 2026-09-24
- **project_revision:** ca0bbab (current HEAD at triage time)
- **observation:** `L-008`'s own `status:` header field read
  `candidate` in `planning/learnings/inbox.md`, despite its own
  curation note (dated 2026-09-11, Phase 43b) stating explicitly
  "**Outcome: retain**, not promote" with a full reasoned disposition.
  That mismatch survived every subsequent phase's own step-10 triage
  pass and the Phase 47/55 bulk reviews — roughly 57 phases — until
  Phase 68's `release-phase-auditor` happened to read the full
  learnings queue end to end for an unrelated purpose (a
  domain-corpus-staleness sweep) and noticed the field disagreed with
  the prose next to it. No process step or mechanical check exists
  whose job is specifically to catch this: `scripts/check_user_docs.py`'s
  `check_promoted_learnings_logged` (L254-273) cross-references
  `status: promoted` against `planning/learnings/promoted.md`, but nothing
  cross-references a `retain`/`merge`/`discard` curation-note verdict
  against its own `status:` field. Spot-checking every other
  `Outcome: retain`-verdict candidate in the current queue
  (`grep -n "Outcome: retain"` across `inbox.md`) found all of them
  correctly carry `status: retained` — so this was a genuine one-off
  miss, not a systemic pattern already in effect across the queue —
  but the check gap that let it go undetected for ~57 phases is itself
  real and would let a *future* instance go undetected the same way,
  regardless of how rare the underlying typo turns out to be.
- **evidence:** `planning/retros/_audit-phase-68.md` §5; `planning/learnings/inbox.md`
  `L-008` entry (status field corrected to `retained` in this same
  triage pass to match its own already-recorded Phase 43b "Outcome:
  retain" verdict); `scripts/check_user_docs.py:254-273`
  (`check_promoted_learnings_logged`, the only existing status
  cross-check, scoped to `promoted` only); `grep -n "Outcome: retain"
  planning/learnings/inbox.md` cross-checked against each match's own
  `status:` field (all other instances already consistent, confirming
  this was an isolated miss rather than a queue-wide problem).
- **classification:** invariant
- **status:** promoted
- **recurrence:** first occurrence (of the meta-gap; `L-008` is the
  single confirmed instance the gap allowed to go undetected so far)
- **curation (Phase 68 triage, 2026-09-24, knowledge-curator):**
  provenance accepted and independently re-verified — re-read
  `check_user_docs.py`'s full set of learnings-queue checks
  (`check_learnings_candidate_fields`, `check_promoted_learnings_logged`,
  `check_stale_evidence_gathering`) directly rather than taking the
  audit report's characterization on trust; confirmed none of the three
  checks a curation-note "Outcome:" verdict against the `status:`
  header for the `retain`/`merge`/`discard` cases. Applied the L-008
  fix inline as part of this same triage pass (status header now reads
  `retained`, matching its own long-standing curation note) — that part
  is the mechanical, one-off correction the Phase 68 retro correctly
  called non-generalizable on its own. The check-coverage gap that let
  it sit uncaught for ~57 phases is the separate, genuinely
  learning-shaped thing the retro's "Candidate learnings filed: None"
  call missed: it is specific (a named code location and a concrete
  blind spot), evidenced (one real instance, one real absence in the
  check's own coverage), and has a cheap, well-scoped destination — not
  an "uncertain but plausible" retain. **Outcome: promote-recommendation**
  (not yet promoted — no artifact has landed; the curator has no write
  access to `scripts/`/`tests/`). Recommending a narrow, low-risk check
  rather than a general-purpose "verify every Outcome" parser (avoiding
  over-fitting the fix to more cases than the one actually observed,
  matching this queue's own `L-008` precedent about calibrating a
  pattern-match check against real false-positive risk before
  generalizing it):
  - **Preferred fix (invariant → test, `scripts/check_user_docs.py` +
    `tests/test_check_user_docs.py`, lead/`docs-maintainer` finalizes):**
    add `check_learnings_status_matches_retain_outcome`, scoped
    narrowly to the one verdict shape actually observed going stale —
    a candidate whose most recent curation note contains
    `Outcome: retain` (optionally followed by ", not promote" /
    ", not promote yet" — the phrasings already in use across this
    file) but whose `status:` header is still `candidate` or
    `evidence-gathering` rather than `retained`:
    ```python
    def check_learnings_status_matches_retain_outcome(root: Path) -> list[Finding]:
        """A candidate whose own curation note records an 'Outcome: retain'
        verdict should carry `status: retained`, not still
        `candidate`/`evidence-gathering` -- the drift L-008 sat with,
        undetected, for ~57 phases (Phase 68 audit finding, L-043)."""
        findings: list[Finding] = []
        for cand_id, body in _iter_learning_candidates(root):
            status_match = re.search(
                r"\*\*status:\*\*\s*([a-z:_-]+)", body, re.IGNORECASE
            )
            status = status_match.group(1).lower() if status_match else ""
            if (
                re.search(r"Outcome:\s*\*{0,2}\s*retain\b", body, re.IGNORECASE)
                and status in ("candidate", "evidence-gathering")
            ):
                findings.append(
                    Finding(
                        "learnings_status_matches_retain_outcome",
                        f"candidate {cand_id} curation note records an "
                        f"'Outcome: retain' verdict but status is still "
                        f"`{status}`",
                    )
                )
        return findings
    ```
    Register it alongside the other learnings-queue checks (near
    `check_promoted_learnings_logged`) and in the script's `CHECKS`
    list. Pair with two regression tests in `tests/test_check_user_docs.py`
    (sibling to the existing `TestPromotedLearningsLogged`-style
    fixtures): (1) a fixture candidate block with `**status:** candidate`
    and a curation note containing `**Outcome: retain**` -> asserts a
    finding is produced; (2) the same block with `**status:** retained`
    -> asserts no finding (the already-correct, common case, to guard
    against a false-positive on every other already-consistent entry in
    this very file).
  - **Rejected alternative:** a fully general check that also parses
    `promote`/`merge`/`discard` verdicts and their corresponding status
    values. Rejected as the *initial* fix — `promote` verdicts
    legitimately stay non-`promoted` until an artifact lands (see
    `L-011`'s own history: `Outcome: promote-recommendation` sat under
    `status: retained`-shaped states for phases before the real
    `promoted_to` commit landed and `status` flipped to `promoted`), so
    a naive "Outcome: promote implies status: promoted" rule would
    false-positive on every legitimate promote-recommendation-not-yet-
    landed candidate in this file today (e.g. `L-010`, `L-011`,
    `L-013`, `L-023`'s own promote-recommendation-shaped entries at
    various points in their history). `retain` has no such legitimate
    lag — once a curator writes "Outcome: retain," the status field
    should already say `retained` in the very same edit — so it is the
    one verdict shape safe to check mechanically without a
    landed-artifact confound. `merge`/`discard` are deferred for the
    same reason (not yet observed going stale, and would need their own
    false-positive calibration first, per `L-008`'s own governing
    lesson about designing a prose-matching check's false-positive case
    before its true-positive one).
  - Not the curator's place to land either the check or its tests —
    both are `scripts/`/`tests/` edits outside this agent's write
    boundary (`planning/learnings/**`, `planning/context-gaps/**`,
    `planning/context-observations/**`, `planning/knowledge/**`, draft
    files under `planning/` only).
- **promoted_to:** `scripts/check_user_docs.py::check_learnings_status_matches_retain_outcome`
  + `tests/test_check_user_docs.py::TestLearningsStatusMatchesRetainOutcome`
  — landed by the lead

### L-042 — the fresh-agent acceptance test's criterion 1 cannot cleanly separate "agent discovered the process" from "the platform auto-loaded CLAUDE.md," a structural confound the current protocol text doesn't disclose or address

- **origin:** Phase 67 retro (final validation) "What didn't work"
  bullet 2 and "Lessons learnt" bullet 2, and `planning/phase-67-final-validation.md`
  §8 sub-task 4's own criterion-1 report — filed by `knowledge-curator`
  on independent review, per this project's own established precedent
  of not accepting a retro's own "described but deliberately left for
  independent triage" framing at face value (`L-035`/`L-036`, `L-038`,
  `L-039`), and per this specific Phase 67 dispatch's own explicit
  instruction to assess this item independently rather than default to
  either "file it" or "nothing to file"
- **date:** 2026-09-24
- **project_revision:** `2b4261e`
- **observation:** Phase 67's fresh-agent acceptance test (protocol
  specified in `planning/v1-redefinition/roadmap.md`'s own Phase 67
  entry, added 2026-09-20 per direct user instruction, and echoed in
  `planning/v1-redefinition/development-methodology.md`) scored 4/4 PASS,
  but criterion 1 ("did it discover that this project has a development
  process at all, and find where it's described") carries an
  honestly-disclosed caveat the lead's own report states plainly:
  `CLAUDE.md` is very likely auto-loaded into any Claude Code session
  operating in this repository by the platform itself, not discovered
  through the dispatched agent's own initiative — a structural property
  of running this specific test on this specific platform (Claude
  Code), not a finding about CodeCompass's own documentation's
  discoverability. Independently verified this is a genuine protocol
  gap, not something already covered: read
  `planning/v1-redefinition/roadmap.md`'s full Phase 67 entry
  (lines 1741-1808) and `development-methodology.md`'s own fresh-agent-
  test paragraph (lines 458-468) directly — neither mentions Claude
  Code, CLAUDE.md auto-loading, or any platform caveat anywhere; both
  specify criterion 1 exactly as "discover... find where it's described"
  with no qualification. Grepped `decisions/` for "fresh-agent
  acceptance test" / "fresh agent" and found **no match at all** — the
  test protocol's actual authoritative text lives only in the two
  planning documents above (`decisions/0060` itself, read in full,
  never names or specifies this test — it is a same-day, separately
  recorded direct-user-instruction amendment to the roadmap, not part of
  that ADR's own Decision section). The roadmap's own text ("Phase 67 is
  meant to validate the methodology once") does not rule out a repeat,
  and gives no guidance for what a repeat should do differently about
  criterion 1's platform confound if one is ever run. The other three
  criteria (locate domain material; recognise unresolved uncertainty;
  produce a grounded design) are unaffected — they test discovery of
  content no platform auto-loads.
- **evidence:** `planning/retros/phase-67-final-validation.md` "What
  didn't work" bullet 2 and "Lessons learnt" bullet 2 (verbatim
  disclosure and generalization, explicitly left unfiled);
  `planning/phase-67-final-validation.md` §8, sub-task 4, criterion 1's
  own report paragraph (the caveat as originally stated by the lead
  reading the fresh agent's actual transcript, not the agent's
  self-summary); `planning/v1-redefinition/roadmap.md` lines 1741-1808
  (the full, current Phase 67 protocol text, read directly — confirmed
  no platform-caveat language exists anywhere in it);
  `planning/v1-redefinition/development-methodology.md` lines 458-468
  (the same test described more briefly, same absence confirmed);
  `decisions/0060-scope-plan-domain-design-implement-methodology.md`
  (read in full — confirms the fresh-agent test is not actually
  specified in this ADR's own Decision section, only cross-referenced
  loosely by Phase 67's plan as "decisions/0060's own amendment,
  2026-09-20"); a direct grep for "fresh-agent acceptance test" / "fresh
  agent" across `decisions/` returning no files.
- **classification:** future-improvement
- **status:** promoted
- **recurrence:**
- **promoted_to:** `planning/v1-redefinition/roadmap.md` Phase 67
  entry (new caveat paragraph) + `development-methodology.md`'s
  fresh-agent-test paragraph (cross-reference)
- **curation (this triage, 2026-09-24, knowledge-curator):** provenance
  accepted — assigned this id, all required fields present.
  Independently re-verified the retro's own account rather than taking
  it on trust: read `planning/v1-redefinition/roadmap.md`'s full Phase
  67 entry and `development-methodology.md`'s fresh-agent-test paragraph
  directly, confirmed neither discloses the platform-auto-load confound
  anywhere; independently confirmed via grep that the "fresh-agent
  acceptance test" is not actually defined inside `decisions/0060` at
  all (it is a same-day roadmap amendment referencing that ADR's
  context, not ADR text itself) — a small but real correction to how the
  dispatch task described this candidate's likely destination.
  **Assessed as genuinely learning-shaped, not a one-off with nowhere to
  land.** The dispositive fact is the roadmap's own text ("Phase 67 is
  meant to validate the methodology once... does not rule out repeating
  it") — this is not a closed, one-time test description the way, say, a
  single phase's own internal report would be; it is a **standing
  protocol** (specified once, in `roadmap.md`, reusable by reference for
  any future repeat) with a real, structural, non-obvious methodological
  flaw in one of its four criteria that the next person to run it would
  otherwise silently reproduce, having no reason to know Phase 67 already
  found and disclosed it. This is exactly the "worth recording for
  whoever designs a repeat" shape the retro itself named but declined to
  operationalize. Considered discarding as "no current trigger, so
  nothing to promote into yet" (the same reasoning that makes `retain`
  appropriate for a merely-plausible, not-yet-actionable observation) —
  rejected: unlike a `retain`-shaped uncertain claim, there is nothing
  uncertain about this finding (the confound is a disclosed, verified
  structural fact, not a hypothesis needing more evidence), and the
  destination is concrete and cheap (a caveat paragraph in an existing,
  already-written protocol section) rather than requiring a new
  mechanism to be invented before it can be actioned. This is the same
  shape `L-031`/`L-032` used to justify `future-improvement` classified
  into `planning/ROADMAP.md`'s backlog rather than `retain`: real,
  evidenced, small, with a clear eventual home, just not urgent because
  no phase currently plans to repeat the test. Checked for a
  merge/duplicate: grepped `inbox.md`/`promoted.md` for "fresh-agent" /
  "CLAUDE.md auto-load" / "platform caveat" — no existing candidate
  covers this. **Outcome: promote**, classification `future-improvement`
  (a protocol note attached to unscheduled future work, not an
  immediately-actionable rule), destination the Phase 67 protocol text
  itself rather than a generic backlog row — closer to the table's
  "future improvement → a roadmap row" mapping than to `workflow`
  (nothing about the 14-step per-session procedure needs to change; the
  gap is in a specific, occasionally-reused test protocol's own written
  criteria). Finalised by the lead / `roadmap-context-curator` — not
  landed here, outside this role's write boundary for `planning/v1-redefinition/roadmap.md`.
  Status left as `candidate` until the amendment is actually applied and
  a `promoted.md` line is added, per `learning-lifecycle.md` §4/§6.

  **Recommended amendment — `planning/v1-redefinition/roadmap.md`'s
  Phase 67 entry** (draft, for the lead to review and land; not applied
  here — insert as a new paragraph immediately after the existing
  "Clarified 2026-09-20... two separate claims, two separate
  consequences" paragraph):

  > **Noted for any repeat of this test (Phase 67 — `L-042`):**
  > criterion 1 ("discover that this project has a development process
  > at all, and find where it's described") cannot cleanly separate the
  > dispatched agent's own initiative from Claude Code's own platform
  > behaviour of very likely auto-loading `CLAUDE.md` into any session
  > operating in this repository — a structural confound of running this
  > specific criterion on this specific platform, not a signal about
  > CodeCompass's own documentation's discoverability. If this test is
  > ever repeated, either (a) report criterion 1 as structurally
  > confounded rather than a clean PASS/FAIL on this platform, or (b)
  > redesign its dispatch (e.g. a harness/agent context that does not
  > auto-load `CLAUDE.md`) to get a genuine discovery signal. Criteria
  > 2-4 are unaffected — none of their target material is platform
  > auto-loaded.

  Also worth a one-line cross-reference from
  `planning/v1-redefinition/development-methodology.md`'s own
  fresh-agent-test paragraph (lines 458-468) back to this note, so a
  reader consulting the methodology doc alone also sees it. Revisit only
  if a repeat is actually scheduled — at that point this note should
  move from "recorded caveat" to an actual criterion-1 redesign decision.

### L-041 — `context-health-planner`'s own charter already promises a "stage boundaries" dispatch cadence that `agent-led-workflow.md`'s actual operational step never carries — the standing trigger exists in name only, across two governing docs, not zero

- **origin:** Phase 67 retro (final validation) "What didn't work" and
  "Process-improvement feedback" — filed by `knowledge-curator` on
  independent review, per this project's own established precedent of
  not accepting a retro's own "described but deliberately left for
  independent triage" framing at face value (`L-035`/`L-036`, `L-038`,
  `L-039`), and per this specific Phase 67 dispatch's own explicit
  instruction to check whether something already covers this before
  treating the retro's "consider a new trigger" framing as the right
  diagnosis
- **date:** 2026-09-24
- **project_revision:** `2b4261e`
- **observation:** `planning/context-health.md`/`planning/context-use-log.md`
  went 21 phases (46-66) with no update, found only because Phase 67's
  own plan happened to name them explicitly. The retro frames this as
  "nothing in `agent-led-workflow.md`'s 14 steps schedules a periodic
  re-check" and suggests `knowledge-curator` consider "a periodic
  `context-health-planner` dispatch trigger... similar to how
  `L-034`/`L-038` added triggers for other files." **Independently
  checked this framing directly and found it materially incomplete**: a
  "stage boundaries" cadence is not merely *absent* — it is **already
  declared, twice, in the roster's own governing documents**, and simply
  never made it into the one document that actually drives what the
  lead does each session. `.claude/agents/context-health-planner.md`'s
  own frontmatter `description` field states verbatim: "Runs at stage
  boundaries and before any phase that leans on CodeCompass context."
  `planning/v1-redefinition/agent-led-development.md` §2.9's own
  "Active in" line, independently read, states the identical cadence:
  "stage boundaries; before any phase that leans on CodeCompass
  context." But `planning/agent-led-workflow.md` step 4 — the actual
  14-step per-session procedure `CLAUDE.md` §8 names as governing —
  names only "Before a phase that leans on CodeCompass context...
  dispatch `context-health-planner`," with **no "stage boundaries"
  language anywhere in the document** (confirmed by a direct grep for
  "stage boundar" returning zero matches in `agent-led-workflow.md`,
  against seven other files that do carry the phrase). This reframes the
  finding from "no trigger exists, invent one" (the retro's framing) to
  "a trigger already exists in the role's own charter and its own
  catalogue entry, but was never operationalized into the step sequence
  that actually executes it" — the fix is alignment, not invention.
  Cross-checked against real phase history
  (`planning/v1-redefinition/roadmap.md`) to confirm this gap is
  recurring, not hypothetical: at least three genuine stage transitions
  fall inside the 46-66 stale window — Stage C's own close (Phase 51,
  GATE DC resolved), Stage D's effective close with Stage E never funded
  and Stage F beginning (around Phase 55b/60), and Stage F's close into
  Stage G (Phase 63/63D → 64) — none of which triggered a
  `context-health-planner` dispatch per `planning/context-health.md`'s
  own last-substantive-update date (Phase 45, per Phase 67's own plan
  §1), confirming the missed cadence is not a single occasion but a
  standing, repeated gap across the entire window.
- **evidence:** `.claude/agents/context-health-planner.md` lines 9-10
  (frontmatter `description`, "Runs at stage boundaries..." — read
  directly); `planning/v1-redefinition/agent-led-development.md` §2.9,
  lines 210-211 ("Active in: stage boundaries; before any phase that
  leans on CodeCompass context" — read directly, independently
  corroborating the agent brief's own claim rather than relying on it
  alone); `planning/agent-led-workflow.md` (read in full at this
  triage) step 4's own text (only the context-leaning-phase trigger,
  no stage-boundary language) and a direct grep for "stage boundar"
  across the repository, confirming `agent-led-workflow.md` is the one
  of eight matching-context files that does *not* contain the phrase;
  `planning/retros/phase-67-final-validation.md` "What didn't work" and
  "Process-improvement feedback" (the retro's own framing, quoted
  above); `planning/phase-67-final-validation.md` §1 and §8 sub-task 1
  (the 21-phase staleness finding and its fix); `planning/v1-redefinition/roadmap.md`
  (the stage-boundary phase ranges cited above, read directly to confirm
  their existence within the 46-66 window).
- **classification:** workflow
- **status:** promoted
- **recurrence:**
- **promoted_to:** `planning/agent-led-workflow.md` step 4 (new bullet:
  dispatch `context-health-planner` at every stage boundary, not only
  before a context-leaning phase)
- **curation (this triage, 2026-09-24, knowledge-curator):** provenance
  accepted — assigned this id, all required fields present.
  Independently verified every claim above rather than taking the
  retro's or the dispatch instruction's framing on trust: read
  `.claude/agents/context-health-planner.md`'s frontmatter directly,
  independently read `agent-led-development.md` §2.9 (not cited by the
  retro at all — found by this triage's own check for "does something
  already cover this"), and read `agent-led-workflow.md` in full,
  confirming by direct grep that "stage boundar" appears in seven other
  project files but not in it. **This changes the correct fix from what
  the retro proposed.** The retro's own "Process-improvement feedback"
  suggests `knowledge-curator` consider *inventing* a periodic-dispatch
  trigger "similar to `L-034`/`L-038`" — but `L-034`/`L-038` both
  addressed a genuine *absence* (no rule existed anywhere). Here, the
  rule already exists, worded identically, in two separate governing
  documents (`context-health-planner.md`'s own charter and
  `agent-led-development.md`'s roster catalogue) — it simply was never
  carried into `agent-led-workflow.md`'s own step sequence, the one
  document that actually drives session-by-session behaviour per
  `CLAUDE.md` §8. This is a *documentation-alignment* gap of the same
  general shape as `L-036` (a brief drifting behind an ADR) but
  differently directed: there, a rarely-exercised brief lagged behind a
  newer decision; here, a cadence stated in a role's own definition (and
  independently repeated in the roster catalogue) was apparently never
  transcribed into the operational step list in the first place, so it
  had no chance to lag — it simply never arrived. Weighed against this
  project's discard precedents (`L-014`/`L-030`): those involved a
  general principle already being *operationally correct* and merely
  under-applied by a lapse in care; here, by contrast, the operational
  document (`agent-led-workflow.md`) is **incomplete relative to its own
  sibling documents**, a structural gap a future lead has no way to
  notice without independently cross-reading three separate files, which
  is exactly what happened for 21 real phases. Checked for a
  merge/duplicate: grepped `inbox.md`/`promoted.md` for
  "context-health-planner"/"stage boundary"/"stage boundaries" — no
  existing candidate or promotion names this specific cross-document gap.
  Not a duplicate of `L-036` (that entry is about a *milestone-scoped
  agent brief drifting behind an ADR it should have incorporated*; this
  one is about a *cadence stated in a role's own charter never being
  transcribed into the step sequence that would actually invoke it* — no
  ADR is involved on either side). **Outcome: promote.** Classification
  `workflow` maps to `planning/agent-led-workflow.md`, matching this
  project's own established practice (every prior `workflow`-classified
  promotion in `promoted.md` landed there). Finalised by the lead — not
  landed here, outside this role's write boundary for that file. Status
  left as `candidate` until the lead actually applies the amendment
  below and a `promoted.md` line is added, per `learning-lifecycle.md`
  §4/§6.

  **Recommended amendment — `planning/agent-led-workflow.md` step 4**
  (draft, for the lead to review and land; not applied here — insert as
  a new bullet immediately after the existing "Before a phase that leans
  on CodeCompass context... dispatch `context-health-planner`..."
  bullet):

  > **Also dispatch `context-health-planner` at every stage boundary**
  > (Stage C→D, the Stage E-skipped transition into Stage F, Stage F→G,
  > and any future boundary `planning/v1-redefinition/roadmap.md`'s own
  > stage grouping defines) — not only immediately before a phase that
  > leans on CodeCompass context. This closes a real gap between the
  > role's own charter (`.claude/agents/context-health-planner.md`'s
  > frontmatter, and `agent-led-development.md` §2.9, both already state
  > "stage boundaries" as part of this role's cadence) and this step's
  > own prior text, which named only the context-leaning-phase trigger —
  > the cadence existed in name, in two documents, but was never
  > operationalized here. Confirmed necessary at Phase 67 (`L-041`):
  > `planning/context-health.md`/`context-use-log.md` went 21 phases
  > (46-66), spanning at least three real stage boundaries, without an
  > update, because nothing in this step ever invoked the cadence the
  > role's own definition already promised. A stage boundary with no
  > material change since the last assessment is a valid dispatch
  > outcome too — an explicit one-line "no action — nothing changed
  > since the last assessment" entry in `planning/context-health.md`'s
  > own History section is sufficient; this bullet does not require a
  > full re-assessment report every single time, only that the check
  > actually happens.

  Revisit toward a mechanical check (e.g. `check_user_docs.py` flagging
  `context-health.md`'s own last-entry date against
  `planning/v1-redefinition/roadmap.md`'s current stage) only if this
  prose trigger proves insufficient at a future stage boundary.

### L-040 — a phase's own final closeout commits (ROADMAP.md/CONTEXT.md status bumps) can reintroduce domain-corpus staleness after the freshness reconciliation already ran and passed

- **origin:** Phase 66's own final independent `release-phase-auditor`
  DoD audit (`planning/retros/_audit-phase-66.md`), non-blocking
  observation 1
- **date:** 2026-09-24
- **project_revision:** `7c85866`
- **observation:** Phase 66's own `domain-skeptic` dispatch (commit
  `b7d0bf3`) independently verified `planning/CONTEXT.md` no longer
  contained the word "connector" after that file's rewrite — true at
  the time. This phase's own later closeout commit (`17e9de6`, the
  same commit that flipped `ROADMAP.md`/the plan file's own Status
  lines to `done`, applying `L-034`/`L-038`'s own lesson) added a
  sentence to `CONTEXT.md`'s "What was just completed" naming
  `docs/domain/concepts/connector.md` by filename — reintroducing a
  literal "connector" match in `CONTEXT.md`, uncaught, because nothing
  re-runs the domain-corpus freshness check after a phase's own final
  status-bump commit. The `release-phase-auditor`'s own independent
  audit caught it (a `grep -i "connector" planning/CONTEXT.md` during
  its own re-verification), and judged it non-substantive (a
  self-referential filename mention, not a use of "connector" as a
  research-candidate term — `connector.md`'s own core claim is
  unaffected) — but the *mechanism gap* is real: this project's own
  domain-corpus freshness reconciliation (added Phase 63D,
  `development-methodology.md`'s "Domain-corpus freshness and
  reconciliation" section) currently runs once, mid-phase, with no
  step re-checking after the phase's own remaining closeout commits
  land.
- **evidence:** `planning/retros/_audit-phase-66.md` (the auditor's own
  finding, non-blocking observation 1, with its own reasoning for why
  this instance is non-substantive); `planning/retros/_domain-freshness-reconciliation-phase-66.md`
  (the earlier, correct "clean" finding, timestamped before commit
  `17e9de6`); commit `17e9de6`'s own diff (the sentence that
  reintroduced the match); `planning/v1-redefinition/development-methodology.md`'s
  own "Domain-corpus freshness and reconciliation" section (names three
  checkpoints — a per-phase drift-audit flag, the phase's own retro,
  and Phase 65's own milestone reconciliation — none of which is
  "after this phase's own final closeout commit," a distinct point in
  the sequence from all three).
- **classification:** workflow
- **status:** promoted
- **recurrence:**
- **promoted_to:** `planning/v1-redefinition/development-methodology.md`
  "Domain-corpus freshness and reconciliation" (new checkpoint 4) +
  `.claude/agents/release-phase-auditor.md` checklist (new item 9)
- **curation (this triage, 2026-09-24, knowledge-curator):** provenance
  accepted — all required fields present. This entry was filed by the
  lead directly from an auditor's own finding, not yet independently
  reviewed by `knowledge-curator` before this pass — reviewed here on
  its own merits rather than deferred, per this dispatch's own explicit
  instruction. Independently re-read
  `planning/v1-redefinition/development-methodology.md`'s "Domain-corpus
  freshness and reconciliation" section (lines 367-407) in full and
  confirmed the entry's own account of it is accurate: exactly three
  checkpoints are named (per-phase drift-audit flag, the phase's own
  retro, Phase 65's own milestone reconciliation), and none of the three
  is scoped to "after the phase's own truly final closeout commit" —
  the first two operate mid-phase (before the final `ROADMAP.md`/
  `CONTEXT.md` status-bump lands per `agent-led-workflow.md` steps 9/11),
  and the third is a milestone-level pass, not a per-phase one. The
  underlying mechanism gap is real and specific: a phase's own final
  closeout commit (the one that flips status lines per
  `agent-led-workflow.md` step 14, applying `L-034`/`L-038`'s own
  lesson) can itself add prose to `CONTEXT.md` — and nothing re-runs the
  domain-staleness check against that specific, last commit. This is the
  same general shape as `L-034` (a real gap in *when*, precisely, a
  check happens relative to the sequence's own final commits) rather
  than a new failure mode. Checked for a merge/duplicate: not a
  duplicate of `L-034` (that entry is about `CONTEXT.md`/`ROADMAP.md`/a
  plan file's Status line disagreeing with each other after
  implementation; this one is about a domain-corpus-staleness term being
  *reintroduced* by the closeout commit's own new prose, a content
  check, not a status-line-agreement check) or of the three checkpoints
  already named in `development-methodology.md` (confirmed distinct
  above). Weighed severity: low in this specific instance (the auditor's
  own account judges the reintroduced match non-substantive — a
  self-referential filename, not a live use of "connector" as a
  research-candidate term) but the *mechanism* gap is real, cheap to
  close, and would not necessarily be caught non-substantively next
  time. **Outcome: promote.** Classification `workflow` maps to
  `planning/v1-redefinition/development-methodology.md`'s own
  "Domain-corpus freshness and reconciliation" section (a fourth,
  explicit checkpoint) — the more precise destination than
  `agent-led-workflow.md` itself, since the three existing checkpoints
  this one extends already live there, not in the generic 14-step
  document. Finalised by the lead — not landed here, outside this
  role's write boundary for that file. Status left as `candidate` until
  the lead actually applies the amendment below and a `promoted.md` line
  is added, per `learning-lifecycle.md` §4/§6.

  **Recommended amendment — `planning/v1-redefinition/development-methodology.md`'s
  "Domain-corpus freshness and reconciliation" section** (draft, for the
  lead to review and land; not applied here — insert as a fourth
  numbered checkpoint, after the existing "3. Knowledge reconciliation —
  Phase 65" item):

  > 4. **Final closeout re-check** (`agent-led-workflow.md` step 13,
  >    `release-phase-auditor`'s own final DoD pass — unchanged
  >    mechanism, widened scope): before treating a phase's own final
  >    `ROADMAP.md`/`CONTEXT.md` status-bump commit (step 14) as closing
  >    the phase, `release-phase-auditor`'s final pass re-runs the same
  >    domain-staleness term check checkpoint (1) already uses, against
  >    the *full* current repository state — including any reconciliation
  >    prose already staged for that closeout commit — not only the
  >    pre-closeout diff checkpoint (1) covered mid-phase. Confirmed
  >    necessary at Phase 66 (`L-040`): a closeout commit's own new
  >    `CONTEXT.md` sentence reintroduced a domain-corpus staleness term
  >    after the mid-phase reconciliation had already run clean; only the
  >    auditor's own independent, incidental re-check caught it.

  Also worth a one-line cross-reference in
  `.claude/agents/release-phase-auditor.md`'s own checklist, so the
  auditor's brief names this explicitly rather than relying on it being
  caught incidentally, as it was at Phase 66. Revisit toward a mechanical
  check (a `check_user_docs.py` domain-term grep run specifically against
  the closeout commit's own diff) only if a future instance is
  substantive rather than a harmless self-referential mention.

### L-039 — a lead's own dispatch prompt must never suggest an exception to a target agent's own hard, unconditional write-boundary rule, even a plausible-looking one

- **origin:** Phase 66 retro (roadmap + context reconciliation) "What
  didn't work" section and "Lessons learnt" bullet 2 — filed by
  `knowledge-curator` on independent review, per this project's own
  established precedent of not accepting a retro's own "nothing to file"
  call at face value (`L-030`, `L-035`/`L-036`, `L-038`), and per this
  specific Phase 66 dispatch's own explicit instruction to independently
  assess this item rather than trust the retro's "None identified"
  account
- **date:** 2026-09-24
- **project_revision:** `d6a0603`
- **observation:** the lead's own dispatch prompt to `domain-skeptic` for
  the Phase 66 domain-corpus freshness reconciliation task suggested the
  agent could resolve a citation-drift finding itself ("you may resolve
  this yourself... a one-line citation fix is not a change to any
  claim's own meaning"). This directly contradicts `domain-skeptic`'s own
  charter, independently re-read at this triage
  (`.claude/agents/domain-skeptic.md` line 94-100, "Hard rules — write
  boundary"): "You never edit any of these, under any circumstance,
  including to fix something you find wrong — even an obviously-correct
  one-line fix to a concept page is not yours to make; name it instead."
  The charter carves out no exception for a fix that doesn't change a
  claim's meaning — it is unconditional. `domain-skeptic` correctly
  declined the lead's own suggested shortcut and named the exact fix for
  the lead to apply instead
  (`planning/retros/_domain-freshness-reconciliation-phase-66.md` "Not
  fixed here — write-boundary" section: "That restriction is not waived
  by a dispatch instruction proposing otherwise; it is a structural rule
  this role exists to hold, not a discretionary default"). No harm
  resulted, but the dispatch prompt itself was the error, and — checked
  directly — nothing in `planning/agent-led-workflow.md` step 5's own
  existing set of dispatch-prompt cautions (concurrent-`Write` collision
  — `L-018`; fresh-agent-type registry lag — `L-023`; milestone-scoped
  brief drift — `L-036`; cross-cluster consistency pass — `L-035`)
  addresses this specific failure mode: a lead's own prompt content
  contradicting a target role's hard, unconditional write-boundary rule.
  This is a repeatable risk, not specific to `domain-skeptic` — any role
  with an unconditional write-boundary rule (`docs-reconstructor`,
  `context-evaluator`, `release-phase-auditor`, `domain-skeptic` again)
  is equally exposed to a future lead drafting the same kind of
  "surely this small case is fine" suggestion into a dispatch prompt.
- **evidence:** `planning/retros/phase-66-roadmap-context-reconciliation.md`
  "What didn't work" (verbatim dispatch-prompt quote) and "Lessons learnt"
  bullet 2 (the generalization, correctly stated but not filed:
  "don't suggest an exception to it in the dispatch prompt, even for what
  looks like an obviously-safe case... a real (if harmless-this-time)
  drafting mistake, not a neutral suggestion the agent is free to take or
  leave"); `planning/retros/_domain-freshness-reconciliation-phase-66.md`
  "Not fixed here — write-boundary" section (the agent's own account of
  declining and naming the fix instead); `.claude/agents/domain-skeptic.md`
  lines 94-100, read directly at this triage (the exact, unconditional
  charter text quoted above — confirms the retro's paraphrase rather than
  taking it on trust); `planning/agent-led-workflow.md` step 5, read
  directly at this triage in full (confirms the four existing
  dispatch-prompt cautions there — `L-018`/`L-023`/`L-036`/`L-035` — none
  of which cover a lead's own prompt inviting a write-boundary exception).
- **classification:** workflow
- **status:** promoted
- **recurrence:**
- **promoted_to:** `planning/agent-led-workflow.md` step 5 (new
  dispatch-prompt caution: never suggest an exception to a target
  agent's own hard write-boundary rule, however plausible-looking)
- **curation (Phase 66 triage, 2026-09-24, `knowledge-curator`):**
  provenance accepted — assigned this id, all required fields present.
  Independently assessed the retro's own "Candidate learnings filed:
  None" call on its merits rather than deferring to it, exactly as
  `CLAUDE.md` §8 requires and exactly as prior triage did for the
  equivalent calls this same retro cites as precedent (`L-030`,
  `L-035`/`L-036`, `L-038`). **Disagree with the retro's own "no new
  mechanism needed" framing.** The retro's "Process-improvement feedback"
  section reasons: "None beyond the lesson above — no new mechanism
  needed, just care when drafting future `domain-skeptic` dispatch
  prompts." This is the same shape of reasoning `L-038`'s triage already
  found insufficient: the general principle (an agent's charter is
  authoritative over a lead's own suggestion) already existed and even
  held on this occasion, but nothing *operationalizes a check on the
  lead's own dispatch-prompt drafting* at the point where the mistake is
  actually made — the same location (`agent-led-workflow.md` step 5) that
  already carries four analogous dispatch-prompt cautions for other
  failure modes discovered exactly this way (one incident, no harm
  resulting, but a nameable, low-cost, generalizable fix). Verified this
  is not domain-skeptic-specific: `domain-skeptic` is one of several
  roles in the roster table with an unconditional "never edits" rule
  (`docs-reconstructor`'s read-only mandate toward what it audits;
  `release-phase-auditor`'s and `context-evaluator`'s "its report only"
  write column) — the same drafting mistake could recur against any of
  them, which is why this belongs in the general dispatch-prompt guidance
  (step 5) rather than a `domain-skeptic`-specific brief amendment.
  Weighed severity: lower than `L-038` (no artifact was actually damaged
  here — the agent's own discipline caught it before any write happened)
  but the *mechanism* gap is the same shape and the fix is essentially
  free (one sentence, no new step, no new dispatch). Checked for a
  merge/duplicate: grepped `inbox.md` and `promoted.md` for
  "write-boundary"/"write boundary"/"obviously-correct"/"obviously safe"
  — no existing candidate or promoted entry names a lead's own dispatch
  prompt contradicting a target role's write boundary; not a duplicate of
  `L-033` (that entry is about `domain-skeptic`'s own review *checklist*
  missing a within-page consistency check — a gap in what the agent looks
  for, not in what the lead tells it to do) or of `L-036` (that entry is
  about an agent *brief* drifting behind an ADR, a maintenance gap on the
  brief's own content — not a per-dispatch prompting error). **Outcome:
  promote.** Classification `workflow` maps to
  `planning/agent-led-workflow.md`, matching this project's own
  established practice (every prior `workflow`-classified promotion in
  `promoted.md` landed there). Finalised by the lead — not landed here,
  outside this role's write boundary for that file. Status left as
  `candidate` until the lead actually applies the amendment below and a
  `promoted.md` line is added, per `learning-lifecycle.md` §4/§6.

  **Recommended amendment — `planning/agent-led-workflow.md` step 5**
  (draft, for the lead to review and land; not applied here — insert as a
  new paragraph alongside the existing `L-018`/`L-023`/`L-036`/`L-035`
  dispatch-prompt cautions):

  > **Never suggest, in a dispatch prompt, that a target agent may make an
  > exception to its own hard, unconditional write-boundary rule — even
  > for a case that looks obviously safe.** A role's write-boundary rule
  > (e.g. `domain-skeptic`'s "never edits the approved domain corpus,
  > under any circumstance, including to fix something you find wrong")
  > exists precisely because "this specific case is obviously fine" is a
  > judgment call the role itself is not supposed to make — a dispatch
  > prompt that invites the exception is a real drafting mistake even if
  > the agent's own charter holds and no harm results. Confirmed at Phase
  > 66 (`L-039`): a dispatch prompt to `domain-skeptic` suggested "you may
  > resolve this yourself... a one-line citation fix is not a change to
  > any claim's own meaning"; the agent correctly declined and named the
  > fix instead, but the prompt itself should never have offered the
  > exception. Before dispatching any role with an unconditional
  > "never edits X" or "its report only" write column (the roster table
  > above), re-read the prompt for any suggestion — however small — that
  > the role could act outside that boundary this one time.

  Revisit toward a stronger check (e.g. a `release-phase-auditor` review
  of dispatch prompts themselves, not just their outputs) only if a
  second occurrence shows this prose caution isn't sufficient.

### L-038 — nothing in the 14-step workflow prompts a check of a session-level/environment-provided convention against `CLAUDE.md` before the first commit of a session

- **origin:** Phase 65 retro (architecture + ADR reconciliation) "What
  didn't work" bullet 1 and "Lessons learnt" bullet 1 — filed by
  `knowledge-curator` on independent review, per this project's own
  established precedent of not accepting a retro's own "nothing to file
  here" reasoning at face value (`L-029`/`L-030`, and the Phase 65 task
  dispatch's own explicit instruction to assess this specific item
  independently rather than trust the retro's account)
- **date:** 2026-09-23
- **project_revision:** `9ddf4cd` (Phase 65's own retro commit)
- **observation:** every commit in the Phase 65 session (32 total,
  several already pushed to `origin` by the time the lapse was caught)
  carried a `Co-Authored-By: Claude.../Claude-Session:` attribution
  trailer, directly contradicting `CLAUDE.md` §7's explicit "Commits
  never include an AI assistant as co-author, contributor, or
  attribution trailer... Fixed convention, not reconsidered case by
  case." `CLAUDE.md` was loaded as the session's own highest-precedence
  governing document throughout (its own §0 states "if this file and any
  other guidance... disagree, this file wins"), yet a generic,
  session-level attribution default was followed instead for the
  session's entire duration up to the point of discovery. The lapse was
  caught only when writing a routine mid-phase commit — not by any
  existing mechanical check (`check_user_docs.py` does not check commit
  trailers) or workflow step — and by then, rewriting the already-pushed
  history to fix it would itself be a destructive git action requiring
  explicit confirmation (`CLAUDE.md`'s own git-safety norms), so the
  user's own decision was to stop going forward rather than rewrite
  shared history. The retro's own "Lessons learnt" section already
  states the generalization explicitly ("An explicit, project-specific
  governance rule always outranks a generic environment-level default...
  checking whether a per-session convention conflicts with an
  already-loaded, higher-precedence project file is worth doing the
  first time such a convention is encountered... a standing point of
  vigilance for future sessions on this project, not a one-time fix")
  but its own "Process-improvement feedback" section explicitly declined
  to file this as a candidate learning, reasoning "`CLAUDE.md` already
  states the rule correctly; the fix was behavioral compliance, not a
  documentation or process gap."
- **evidence:**
  `planning/retros/phase-65-architecture-adr-reconciliation.md` "What
  didn't work" bullet 1 and "Lessons learnt" bullet 1 (verbatim
  generalization quoted above; the retro's own explicit non-filing
  reasoning); `CLAUDE.md` §0 ("this file wins" precedence statement) and
  §7 (the rule violated) — both read directly at this triage, confirmed
  currently, correctly, and unambiguously stated, unedited by this
  incident; `planning/agent-led-workflow.md` (read in full at this
  triage) — its 14 steps, including step 1 ("Inspect the repository...
  git log, git status, the test state"), name no check of any
  session-level/environment-provided convention against `CLAUDE.md`
  anywhere in the sequence; this session's own git history, per the
  retro's own explicit count (32 commits, several already pushed) — not
  independently re-counted by this triage (no Bash access; taken from
  the retro's own account, which is itself an admission against the
  lead's own interest and not the kind of claim a retro would inflate).
- **classification:** workflow
- **status:** promoted
- **recurrence:**
- **promoted_to:** `planning/agent-led-workflow.md` step 1 (new
  paragraph: check a session-level/environment convention against
  CLAUDE.md before the first commit of a session)
- **curation (Phase 65 triage, 2026-09-23, knowledge-curator):**
  provenance accepted — assigned this id, all required fields now
  present. Independently assessed the retro's own "nothing to file"
  reasoning on its merits rather than deferring to it, exactly as this
  project's `CLAUDE.md` §8 requires ("An agent observation is not
  authoritative because an agent recorded it" — including a retro's own
  judgment that something isn't candidate-worthy) and exactly as prior
  triage did for Phase 62's and Phase 63's equivalent non-filing calls
  (`L-029`, `L-030`). **Disagree with the retro's own conclusion.** The
  retro's reasoning — "`CLAUDE.md` already states the rule correctly; the
  fix was behavioral, not textual" — is true as far as it goes, but it is
  the same shape of reasoning this project's own workflow-classified
  precedents (`L-006`, `L-013`, `L-018`, `L-023`, `L-034`, `L-035`,
  `L-036`) have repeatedly found insufficient to justify a discard: in
  each of those, the *general* principle already existed somewhere (a
  standing rule, an agent's charter, `CLAUDE.md` itself) but nothing
  *operationalized when to apply it* in the 14-step sequence, and the gap
  was only closed once a concrete trigger point was added to
  `agent-led-workflow.md`. This is the same gap, not a different one:
  `CLAUDE.md` §0/§7 already state the rule's content and precedence with
  total clarity, but no step in `agent-led-workflow.md` ever prompts a
  lead to actually *compare* a session-level default against `CLAUDE.md`
  at a concrete moment — the session ran 32 commits deep, several already
  pushed, before the conflict was noticed, purely because nothing forced
  an earlier look. This is a materially different shape from the discard
  precedents `L-014`/`L-030` (a single lead lapse against an
  already-general, already-operationalized "verify independently, every
  time" instruction, with no plausible concrete trigger-point gap to
  name) — there, the fix genuinely was "just follow the existing rule
  more carefully"; here, a concrete, nameable, low-cost trigger point
  (step 1, session start) is missing and would plausibly have caught this
  before it compounded across 32 commits. Weighed the severity: unlike
  most workflow gaps in this queue, this one left a *permanent*, uncorrected
  artifact (32 already-pushed commits the user explicitly chose not to
  rewrite) — the kind of outcome that argues for closing the gap going
  forward even though this specific instance can't be undone. Checked for
  a merge/duplicate: not a duplicate of any existing candidate (grepped
  `inbox.md` and `promoted.md` for "attribution"/"co-author"/"trailer" —
  no match); distinct from `L-036` (that entry is about a *milestone-scoped
  agent brief* drifting behind a landed ADR — an artifact-staleness gap;
  this one is about a *session-level convention* never being checked
  against `CLAUDE.md` at all — a different failure mode, at a different
  point in the workflow). **Outcome: promote.** Classification `workflow`
  maps to `planning/agent-led-workflow.md`, matching this project's own
  established practice (every prior `workflow`-classified promotion in
  `promoted.md` landed there, not in `.claude/skills/`, despite the
  lifecycle table's literal "workflow → skill" line). Finalised by the
  lead — not landed here, outside this role's write boundary for that
  file. Status left as `candidate` until the lead actually applies the
  amendment and a `promoted.md` line is added, per `learning-lifecycle.md`
  §4/§6.

  **Recommended amendment — `planning/agent-led-workflow.md` step 1
  ("Inspect the repository")** (draft, for the lead to review and land;
  not applied here — insert as a new paragraph):

  > **Before the first commit of a session, check whether any
  > session-level or environment-provided convention (e.g. a default
  > commit-attribution trailer) conflicts with an already-loaded,
  > higher-precedence project rule.** `CLAUDE.md` always wins over a
  > generic environment default per its own §0 — but that precedence
  > only protects the project if something actually prompts the
  > comparison. Confirmed necessary at Phase 65 (`L-038`): a session-wide
  > attribution-trailer default silently contradicted `CLAUDE.md` §7 for
  > 32 commits, several already pushed to shared history before the
  > conflict was noticed and could not be cleanly undone. No mechanical
  > check catches this (`check_user_docs.py` does not inspect commit
  > trailers); only an explicit comparison at session start does.

  Revisit toward a mechanical check (e.g. a pre-push hook or
  `check_user_docs.py` extension scanning recent commit trailers against
  `CLAUDE.md` §7) if a second occurrence shows a prose reminder at step 1
  isn't sufficient to actually catch this before commits accumulate.

### L-037 — a module docstring can carry the exact same history-narration/staleness pattern `documentation-lifecycle.md` targets in current-truth docs, but sits outside any of this project's own doc-drift checks

- **origin:** Phase 65 (architecture + ADR reconciliation), flagged by
  the `docs-maintainer` dispatch executing the `architecture/overview.md`
  reconciliation, while re-verifying `graph.py`'s own cross-reference to
  `architecture/overview.md`'s "Context graph" section (now stale as a
  direct result of this phase's own restructuring)
- **date:** 2026-09-23
- **project_revision:** `b48e7a9`
- **observation:** `src/codecompass/graph.py`'s own module docstring
  stated "**Not called from `sync.py` or `cli.py` yet** — that wiring
  starts in Phase 11 (usage detection) and continues through Phase 15
  (CLI rewire)" — a transitional-state claim that has been false since
  Phase 15 (many phases ago; `sync.py`'s real, current
  `rebuild_project_graph` calls `rebuild_deterministic` directly,
  confirmed live at `sync.py:353`). This is the exact same
  "transitional-state descriptions... should be deleted outright once
  the transition is complete" pattern `architecture-split-candidates.md`
  catalogues by the dozen for `architecture/overview.md` itself
  (e.g. item 26's "still not CLI-visible" framing) — except this
  instance lived inside a `src/codecompass/` module docstring, not a
  current-truth doc, so no existing mechanism (`check_user_docs.py`,
  `docs-reconstructor`'s per-phase drift audit, or Phase 65's own
  `architecture-split-candidates.md` catalogue itself) ever had a reason
  to look at it. Found and fixed opportunistically, alongside the
  citation-target fix this phase's own restructuring required (the
  docstring's own pointer to "architecture/overview.md's 'Context
  graph' section" needed updating regardless, to
  `architecture/context-graph-schema.md`) — not found by any systematic
  search of `src/codecompass/`'s other module docstrings for the same
  pattern.
- **evidence:** `src/codecompass/graph.py:1-11` (pre-fix, commit
  `5d4fa94` and earlier — the false "not called yet" claim, alongside
  the now-stale `architecture/overview.md` citation); `src/codecompass/sync.py:234,353`
  (`rebuild_project_graph`/`rebuild_deterministic`, confirming the real,
  current, long-standing wiring the docstring denied); this phase's own
  `docs-maintainer` dispatch report (flagged this exact finding
  explicitly, "out of my write boundary" since `src/` isn't
  `docs-maintainer`'s to edit); `planning/v1-redefinition/architecture-split-candidates.md`'s
  own "How Phase 65 should use this" section (the transitional-state
  principle this docstring also violates, written for `architecture/overview.md`
  specifically, with no scope note about `src/` docstrings one way or
  the other).
- **classification:** scoped-rule (corrected from the as-filed `open-work`
  at this triage — see curation note below)
- **status:** promoted
- **recurrence:**
- **promoted_to:** `.claude/agents/docs-maintainer.md` "Hard rules" (new
  bullet: when reading a `src/` module docstring to verify or update a
  citation, also scan that same docstring's other claims for the same
  transitional-state staleness pattern, and flag any found even though
  fixing them is outside this role's write boundary)
- **curation (Phase 65 triage, 2026-09-23, knowledge-curator):**
  provenance accepted — all required fields present. Independently
  re-verified rather than taking the retro's/candidate's own account on
  faith, within this role's tool limits (no Bash, so no `git show` of the
  cited pre-fix commit — see below): read the *current* (post-fix)
  `src/codecompass/graph.py:1-20` directly and confirmed it now correctly
  reads "called from `sync.py`'s `rebuild_project_graph` on every
  whole-project `sync`," with no "not called yet" language anywhere.
  Independently confirmed the real wiring the pre-fix docstring is
  claimed to have denied: `sync.py:234` defines `rebuild_project_graph`,
  which calls `rebuild_deterministic` at `sync.py:353` exactly as the
  candidate's evidence field states; `sync.py`'s *own* module docstring
  (line 11) independently corroborates "`rebuild_project_graph` (Phase
  11, extended in..." as the wiring's origin phase; `cli.py` directly
  imports and calls `rebuild_project_graph` at four call sites
  (`cli.py:49,127→136` via `sync_all`+explicit call, `:234`, `:296→300`
  via `sync_all`+explicit call) — the wiring is real, current, and has
  existed since Phase 11, confirming a "not called from `sync.py` or
  `cli.py` yet" claim would indeed have been false for a long time by
  Phase 65. **Limitation honestly disclosed**: this role has no Bash, so
  the literal pre-fix docstring text (cited as `graph.py:1-11`, commit
  `5d4fa94` and earlier) could not be independently retrieved via `git
  show` as the dispatch instruction suggested; the above corroborates the
  claim's *substance* (the wiring is real and long-standing, so a
  "not-yet-wired" claim about it would be false) rather than the exact
  pre-fix wording. Nothing here contradicts the candidate's account, and
  the candidate's own citation of the `docs-maintainer` dispatch report
  as a source (an agent flagging something explicitly out of its own
  write boundary) is plausible on its face.

  **Reclassified from `open-work` to `scoped-rule`.** `open-work` (§4:
  "unresolved current work" → `CONTEXT.md` "next step/outstanding") does
  not fit: the actual instance was already fixed inline this same phase
  (per the retro's own "What was achieved" list) — there is no
  outstanding work-in-progress to record in `CONTEXT.md`. The
  generalizable content is a coverage gap in *who ever looks at* a
  `src/` module docstring's non-citation claims: `docs-maintainer` was
  already physically reading this docstring to fix its citation, and
  caught the separate staleness only opportunistically, not because
  anything in its own charter prompted a look. This is the same shape as
  `L-033` (a within-page consistency check is a distinct axis from a
  claim-against-source check, missed by a charter that only names the
  latter) — not "already covered by an existing general discipline" the
  way `L-014`/`L-030` were discarded (this project's "verify
  independently" standing rule is about checking what you're citing, not
  about proactively re-scanning unrelated parts of a file you're already
  present in for an unrelated reason). Considered `future-improvement`
  (a `ROADMAP.md` row, `L-031`/`L-032`'s destination) as an alternative:
  rejected — those two are `src/` *behavior* gaps needing dedicated
  implementation (a migration, a validation check); this is a *detection
  coverage* gap, cheaply closed by a one-sentence charter addition, not a
  scheduled implementation task. Considered whether this should instead
  widen `docs-reconstructor`'s per-phase drift-audit scope (`CLAUDE.md`
  §5's DoD text explicitly enumerates `README.md`/`docs/`/`architecture/`/
  `ai-docs/` as its checked categories) — rejected as the promotion
  target: that would require amending `CLAUDE.md` §5's own DoD text
  itself (a `project-rule`-classification change, gated on
  `proposed-governance-changes.md` and explicit user approval per
  `CLAUDE.md` §0), a materially larger and riskier lift than the
  `docs-maintainer`-charter addition below for a single-occurrence,
  not-yet-shown-to-be-systemic finding (the candidate's own text
  discloses this was found opportunistically, "not by any systematic
  search of `src/codecompass`'s other module docstrings for the same
  pattern" — real evidence of one instance, not evidence of a widespread
  problem). Checked for a merge/duplicate: not a duplicate of `L-033`
  (different role, different artifact class — a `src/` docstring, not a
  `docs/domain/` corpus page — despite the shared "within-file
  consistency is a distinct check" shape); not a duplicate of any
  `future-improvement` entry (grepped `promoted.md`/`ROADMAP.md` for
  "docstring"/"module docstring" — no match). **Outcome: promote**, on
  the same "specific, well-evidenced, low-cost, first-occurrence"
  reasoning `L-033` used, not recurrence-count. Classification
  `scoped-rule` maps to a `.claude/` agent-brief amendment, finalised by
  the lead (not landed here — outside this role's write boundary).
  Status left as `candidate` (not `promoted`) until the lead actually
  applies the amendment and a `promoted.md` line is added, per
  `learning-lifecycle.md` §4/§6 and this queue's own established practice
  for a promotion whose landing is deferred to the lead (`L-033`,
  `L-031`, `L-032`).

  **Recommended amendment — `.claude/agents/docs-maintainer.md` "Hard
  rules"** (draft, for the lead to review and land; not applied here —
  insert as a new bullet):

  > When reading a `src/` module docstring to verify or update a
  > citation into `architecture/`/`docs/` (something already within this
  > role's normal reconciliation work), also scan that same docstring's
  > other claims — especially transitional-state language ("not called
  > from X yet," "starts in Phase N," "continues through Phase M") — for
  > the same staleness pattern `documentation-lifecycle.md` targets in
  > current-truth docs. Flag anything found to the lead even though
  > fixing a `src/` file is outside this role's own write boundary.
  > Confirmed necessary at Phase 65 (`L-037`): `graph.py`'s own module
  > docstring carried a "not called from `sync.py`/`cli.py` yet" claim
  > that had been false since Phase 11-15, found only opportunistically
  > while this role's own dispatch was already re-pointing that same
  > docstring's citation for an unrelated reason — no existing mechanical
  > check or per-phase audit is scoped to look at `src/` module
  > docstrings at all.

  Revisit toward `future-improvement`/a `docs-reconstructor` scope
  widening (with the accompanying `CLAUDE.md` §5 governance change) only
  if a deliberate future sweep, or a second opportunistic find, shows
  this is systemic rather than a single stale docstring.

### L-036 — a milestone-scoped, rarely-exercised agent brief is a recurring locus of drift behind its own governing ADR, confirmed twice now

- **origin:** Phase 64 retro (blank-slate documentation reconstruction)
  "What worked" bullet 4 and "Lessons learnt" bullet 2 — filed by
  `knowledge-curator` on independent review of the retro's own
  "Candidate learnings filed: None" call, per this project's own
  established precedent (Phase 63's `release-phase-auditor` flagging a
  retro's own non-filing decision as itself a curation judgment
  `CLAUDE.md` §8 reserves for `knowledge-curator`, which produced
  `L-030`)
- **date:** 2026-09-23
- **project_revision:** `3889779`
- **observation:** Twice now, a `.claude/agents/*.md` brief exercised
  only once per milestone (not every phase) was found to have drifted
  behind an already-landed governing ADR, and was caught and fixed by
  the lead while writing the *next* phase's plan, before dispatch —
  not by any mechanical check. First: at Phase 63D, `fef153b` ("agent
  setup: `domain-skeptic` created, `context-researcher`/
  `docs-reconstructor` extended") amended both `context-researcher.md`
  and `docs-reconstructor.md`'s MODE 1 section pre-dispatch. Second: at
  Phase 64, its own plan §1 ("A real, disclosed gap this phase must
  close before dispatching") found `docs-reconstructor.md`'s MODE 2
  section still predated `decisions/0060` — missing both the
  `docs/domain/` consumption exception and the six-category output
  structure that ADR had already settled — and amended it before any
  dispatch. Neither drift was caught by `scripts/check_user_docs.py`
  or any other mechanical check; both were caught only because the
  lead happened to re-read the brief while planning the next phase
  that would use it.
- **evidence:** `planning/phase-64-blank-slate-documentation-reconstruction.md`
  §1 (the disclosed pre-dispatch gap and its fix); commit `fef153b`
  (Phase 63D's own agent-brief extension, same commit cited in
  `planning/retros/phase-63d-domain-reconstruction.md`'s own
  commit list); `planning/retros/phase-64-blank-slate-documentation-reconstruction.md`
  "What worked" bullet 4 and "Lessons learnt" bullet 2 (the explicit
  generalisation: "any agent whose brief is exercised rarely... is more
  likely to have drifted... worth an explicit check at the start of any
  future milestone-scoped dispatch, not just this one"). Checked and
  confirmed absent as a standing rule: no match for "governing ADR" /
  "brief" / "drift" pre-dispatch check in
  `planning/agent-led-workflow.md` or
  `planning/v1-redefinition/documentation-lifecycle.md` (direct grep,
  2026-09-23) — the practice exists only as two ad hoc, phase-specific
  fixes, not a named step any future milestone-scoped dispatch is
  prompted to repeat.
- **classification:** workflow
- **status:** promoted
- **recurrence:** 2 (Phase 63D `fef153b`; Phase 64 plan §1) — this is
  itself the reason to promote now rather than wait for a third.
- **promoted_to:** `planning/agent-led-workflow.md` step 5 (new
  paragraph: re-read a milestone-scoped agent brief against every ADR
  landed since its own last edit, before dispatching it)
- **curation (this triage, 2026-09-23, knowledge-curator):** provenance
  accepted — all required fields present, both cited commits/documents
  independently checked, not taken on the retro's word alone (confirmed
  `fef153b`'s description in the Phase 63D retro's own commit list
  independently, and confirmed the absence of any existing standing
  rule via direct grep rather than assuming the retro's framing was
  novel). This is exactly the shape the learning lifecycle exists for:
  a real, twice-confirmed, low-cost-to-fix structural risk, currently
  surviving only as tribal memory across two lead-authored plan files,
  for a category of agent (`docs-reconstructor` MODE 2, and by the same
  argument any future milestone-scoped role) that is by definition
  exercised too rarely for repetition alone to keep its brief current.
  Correctly *not* filed as a `context-gap` (it is about an agent-brief
  artifact, not a graph relationship) and correctly *not* a duplicate of
  `L-023` (that entry is about a brand-new agent type being
  undispatchable immediately after creation — a registry-timing gap;
  this one is about an *existing* agent's brief drifting behind an ADR
  landed after the brief was last edited — a maintenance gap). **Outcome:
  promote.** Classification `workflow` maps to
  `planning/agent-led-workflow.md`, finalised by the lead. **Landed**:
  see `status`/`promoted_to` above.

  **Amendment landed — `planning/agent-led-workflow.md` step 5**
  (as a new paragraph, alongside the existing L-018/L-023 dispatch
  cautions):

  > **Before dispatching a milestone-scoped agent brief (one exercised
  > once per milestone rather than every phase — e.g. `docs-reconstructor`
  > MODE 2), re-read it against every ADR/decision landed since its own
  > last edit.** A brief exercised rarely is structurally more likely to
  > have drifted behind a later ADR amendment than one exercised every
  > phase, because normal use never forces a re-read. Confirmed twice: at
  > Phase 63D (`context-researcher.md`, `docs-reconstructor.md` MODE 1,
  > both amended pre-dispatch for `decisions/0060`) and at Phase 64
  > (`docs-reconstructor.md` MODE 2, same ADR, same pre-dispatch fix).
  > Neither mechanical check catches this; only re-reading the brief
  > while writing the plan that will dispatch it does. (Phase 64 —
  > `L-036`.)

  Revisit if a third occurrence surfaces despite this addition — that
  would argue for a mechanical check (e.g. a per-agent-brief
  "governing ADRs" front-matter field a script could diff against
  `decisions/` mtimes) rather than a habit alone.

### L-035 — an explicit cross-cluster consistency pass after parallel/multi-cluster dispatches is a repeatable step worth codifying, not an incidental synthesis nicety

- **origin:** Phase 64 retro (blank-slate documentation reconstruction)
  "What worked" bullet 2 and "Lessons learnt" bullet 1, reinforcing a
  pattern first exercised (uncodified) at Phase 63D — filed by
  `knowledge-curator` on the same independent review as `L-036` above
- **date:** 2026-09-23
- **project_revision:** `3889779`
- **observation:** Twice now, a phase that split a large derivation task
  across multiple parallel, independently-dispatched agent clusters
  added a distinct, explicit synthesis step *after* all clusters landed
  — checking for agreement/contradiction/duplication across cluster
  boundaries — and that step caught something no single cluster's own
  review could have. At Phase 63D, dispatching `domain-skeptic` against
  the *integrated* corpus (not each cluster in isolation) is what let it
  catch cross-cluster consistency issues a single cluster's own review
  never would have seen (Phase 63D retro, "What worked" bullet 2). At
  Phase 64, the lead's own explicit cross-cluster consistency pass
  (named in advance in the phase's own plan §2, not added after the
  fact) both confirmed a genuine independent corroboration (Clusters A
  and B independently flagging `docs/external-adapters.md` as a split
  candidate from opposite sides, without reading each other's output)
  and correctly distinguished it from a re-confirmation of an
  already-tracked item (the `ecosystem`/`capabilities` gap vs. `L-032`)
  rather than double-counting either. Neither instance names this as a
  standing, generally-applicable step — each phase's plan named it
  freshly, for that phase only.
- **evidence:** `planning/retros/phase-63d-domain-reconstruction.md`
  "What worked" bullet 2 (`domain-skeptic` dispatched against the
  integrated corpus); `planning/phase-64-blank-slate-documentation-reconstruction.md`
  §2 ("After all three land, the lead reads across all six categories
  for cross-cluster consistency... before closing the phase"); the
  actual Phase 64 output performing this
  (`planning/v1-docs-reconstruction/README.md`'s own "Cross-cluster
  consistency" section, five checks performed); `planning/retros/phase-64-blank-slate-documentation-reconstruction.md`
  "What worked" bullet 2 and "Lessons learnt" bullet 1 (the explicit
  generalisation: "worth doing explicitly, as its own step, even when no
  contradiction is expected"). Checked and confirmed absent as a
  standing rule: no match for "consistency pass" / "cross-cluster" /
  "multi-cluster" in `planning/agent-led-workflow.md` or
  `planning/v1-redefinition/documentation-lifecycle.md` (direct grep,
  2026-09-23).
- **classification:** workflow
- **status:** promoted
- **promoted_to:** `planning/agent-led-workflow.md` step 5 (new
  paragraph: any multi-cluster phase must include an explicit
  post-dispatch consistency pass before closing the phase)
- **recurrence:** 2 (Phase 63D, via `domain-skeptic` against the
  integrated corpus; Phase 64, via an explicit lead synthesis pass) —
  same "why promote now, not after a third" reasoning as `L-036`.
- **curation (this triage, 2026-09-23, knowledge-curator):** provenance
  accepted — all fields present, both cited instances independently
  re-read (not taken on the retro's word alone), absence of a standing
  rule confirmed by direct grep rather than assumed. Not a duplicate of
  `L-018` (that entry is about *never dispatching two agents to `Write`
  the same file concurrently* — a race-condition hazard during parallel
  dispatch; this one is about *what happens after* parallel dispatches
  land, a synthesis-completeness concern, not a write-collision one).
  Not a documentation-content finding (unlike `concepts-to-retire.md`'s
  five candidates) — it is a claim about how *this project itself*
  should structure any future phase that uses parallel/multi-cluster
  dispatch, squarely a workflow finding. Genuinely twice-confirmed
  (Phase 63D, Phase 64), on two differently-shaped tasks (domain
  investigation; documentation structure), by two different mechanisms
  (a dedicated `domain-skeptic` dispatch; a lead-only synthesis pass) —
  the mechanism varies, but "some explicit post-dispatch consistency
  pass, not merely assuming the individual dispatches' own correctness
  composes" is the constant worth naming as a standing expectation
  rather than something each phase's plan must independently
  rediscover. **Outcome: promote.** Classification `workflow` maps to
  `planning/agent-led-workflow.md`, finalised by the lead. **Landed**:
  see `status`/`promoted_to` above.

  **Recommended amendment — `planning/agent-led-workflow.md` step 5**
  (draft, for the lead to review and land; not applied here — insert as
  a new paragraph in step 5, near the existing "One agent = one
  artifact" guidance):

  > **Any phase that splits work across multiple parallel, independently-
  > dispatched agent clusters must include an explicit post-dispatch
  > consistency pass — after all clusters land, before closing the
  > phase — checking for agreement, contradiction, and duplication
  > across cluster boundaries.** This is a distinct step from each
  > cluster's own within-scope correctness, and from any dedicated
  > adversarial-review dispatch (e.g. `domain-skeptic`) that may also
  > run against the integrated result. Confirmed twice: Phase 63D
  > (`domain-skeptic` dispatched against the integrated corpus, not each
  > cluster separately) and Phase 64 (an explicit lead synthesis pass,
  > named in the phase's own plan in advance) each caught something —
  > independent corroboration in one case, a duplicate-vs-corroboration
  > distinction in the other — that no single cluster's own review would
  > have surfaced. (Phase 64 — `L-035`.)

  Revisit if a future multi-cluster phase's plan omits this and the
  omission causes a real miss — that would argue for moving this from a
  workflow habit into a `release-phase-auditor` DoD check (a multi-
  cluster phase's retro must name what its consistency pass found)
  rather than a step description alone.

### L-033 — a within-page consistency check is distinct from a claim-against-source check, and `domain-skeptic`'s own review missed the former

- **origin:** Phase 63D (Domain reconstruction), the actual user's own
  review of the approved corpus, catching what `domain-skeptic`'s own
  independent review pass had not
- **date:** 2026-09-23
- **project_revision:** `27bac36`
- **observation:** `docs/domain/concepts/provenance.md`'s own
  Definition section asserted "the three enrichment tables each carry a
  single `model` column," two paragraphs before its own Counterexample
  section correctly stated `symbol_enrichment` has no such column at
  all — a self-contradiction within one page.
  `evidence.md`'s "Relationships" section repeated the same
  over-generalisation in passing. `domain-skeptic`'s own review report
  (`planning/retros/_domain-skeptic-review-phase-63d.md` §3)
  independently re-verified `provenance.md`'s *Counterexample* claim
  against the real schema and confirmed it accurate, but did not
  separately check whether the same page's own *Definition* section
  agreed with it. The review's own charter names "search for
  contradictions... between two concept pages" explicitly, but does not
  name checking a single page's own sections against each other as a
  distinct pass.
- **evidence:** `docs/domain/concepts/provenance.md` (pre-fix, commit
  `f39a986`, Definition section vs. Counterexample section);
  `docs/domain/concepts/evidence.md` (pre-fix, same commit, Relationships
  section); `planning/retros/_domain-skeptic-review-phase-63d.md` §3
  (the review's own re-verification of the Counterexample claim only);
  `.claude/agents/domain-skeptic.md` step 3 ("search for
  contradictions... between two concept pages," no explicit mention of
  within-page consistency).
- **classification:** scoped-rule
- **status:** promoted
- **recurrence:**
- **promoted_to:** `.claude/agents/domain-skeptic.md` step 3 (within-page
  consistency check added to the contradiction-search instruction)
- **curation (Phase 63D triage, 2026-09-23, knowledge-curator):**
  provenance accepted — all required fields present. Independently
  verified rather than taking the retro's own account on faith: read
  the *current* (post-fix, commit `507e6f6`) `docs/domain/concepts/provenance.md`
  directly and confirmed its Definition section now correctly says "**Two
  of the three enrichment tables** — `vendor_enrichment` and
  `doc_relation_enrichment` — each carry a single `model` `TEXT`
  column... `symbol_enrichment` carries no provenance column at all," in
  agreement with its own Counterexample section — the self-contradiction
  is genuinely fixed, not merely claimed fixed. Independently re-read
  `.claude/agents/domain-skeptic.md` step 3 directly: it names
  "contradictions... between two concept pages in the same corpus" and
  "between the corpus and directly-checkable source/test/ADR content" as
  its two explicit examples — it does not name a page's own sections
  against each other as a third, distinct check. This is a real,
  narrow, well-evidenced gap: `domain-skeptic`'s own review report
  (`_domain-skeptic-review-phase-63d.md` §3) shows it *did* independently
  re-verify the Counterexample section's claim against the real schema
  and correctly confirmed it accurate — the miss was specifically that
  a *different* section two paragraphs earlier, in the same file,
  asserted the opposite, and nothing in step 3's literal text prompted a
  check of that kind. Checked for a merge/duplicate: no existing
  candidate names within-page consistency checking; not a duplicate.
  Weighed against this project's own "single-occurrence, zero-harm,
  already-covered-by-existing-discipline" discard/retain precedent
  (`L-014`, `L-029`, `L-030`) and judged this is a materially different
  shape: those cases involved a *lead* carrying forward a stale planning
  claim despite an already-general "verify independently" rule already
  in force; here, `domain-skeptic`'s own charter *specifically and
  narrowly scopes* its contradiction-search examples to cross-page and
  page-vs-source, on its first real dispatch, for a role whose entire
  purpose (`decisions/0060`) is to reduce exactly this class of
  user-facing review burden — a corpus reached the actual user with an
  internal self-contradiction the review's own explicit checklist gave
  no prompt to catch, even though the review otherwise worked exactly as
  designed (real evidence gathered, one genuine ambiguity resolved with
  git-history evidence, zero false escalations). Given `domain-skeptic`
  is a new, foundational, repeatedly-reused role (already slated for
  Design-stage `design.md` review per its own charter), a one-sentence,
  low-cost charter clarification closing a specific, nameable checklist
  gap is worth landing now rather than waiting for a second occurrence.
  **Outcome: promote.** Classification `scoped-rule` correctly maps to
  a `.claude/` agent-brief amendment, finalised by the lead (not
  landed by this triage — outside this role's write boundary). Status
  left as `candidate` (not `promoted`) until the lead actually applies
  the amendment and a `promoted.md` line is added, per
  `learning-lifecycle.md` §4/§6.

  **Recommended amendment — `.claude/agents/domain-skeptic.md` step 3**
  (draft, for the lead to review and land; not applied here — insert as
  a new sentence at the end of step 3's existing paragraph):

  > Also check a single page's own sections against each other — its own
  > Definition against its own Counterexample, Invariants, or Examples —
  > not only page-against-page or page-against-source. A page's central
  > or counterexample claim checking out against source is not proof the
  > page is internally consistent: confirmed necessary at Phase 63D,
  > where `provenance.md`'s Definition section asserted the opposite of
  > what its own Counterexample section (independently re-verified
  > against the real schema) correctly stated, two paragraphs apart in
  > the same file.

  Revisit/withdraw only if a future review shows this addition still
  isn't sufficiently explicit to catch the next instance (which would
  argue for a stronger structural fix — e.g. an explicit per-page
  "read every section, then re-read the page as a whole for internal
  agreement" step — not merely a discard).

### L-034 — planning-status closeout discipline: `CONTEXT.md` being updated correctly is not evidence that `ROADMAP.md`/the plan file's own Status line were too

- **origin:** Phase 63D (Domain reconstruction) closeout, second
  occurrence — Phase 62's own closeout (`planning/retros/_audit-phase-62.md`
  precedent territory, though that specific finding was about a missing
  audit-report file, not this exact pattern) already surfaced a related
  "did I update every planning-status file, not just the one I'm
  actively narrating" gap
- **date:** 2026-09-23
- **project_revision:** `27bac36`
- **observation:** After Phase 63D's own implementation work completed,
  `planning/CONTEXT.md` was updated correctly to say "corpus complete,
  awaiting actual-user approval," but `planning/ROADMAP.md`'s own Phase
  63D row and `planning/phase-63d-domain-reconstruction.md`'s own
  Status line were both left saying "not started"/"plan only" — caught
  only by the actual user's own review, not by the lead before
  presenting the work. This is the same *shape* of gap as Phase 62's
  own plan-file Status line being left stale after full implementation
  (caught during a dedicated Phase 62 closeout-consistency check, a
  separate session) — a second occurrence of "the actively-narrated
  file (`CONTEXT.md`, or the conversation itself) gets updated; the
  quieter tabular/status-line files do not," not a one-off slip.
- **evidence:** `planning/CONTEXT.md` (commit `27bac36`, correct) vs.
  `planning/ROADMAP.md` row 63D and
  `planning/phase-63d-domain-reconstruction.md`'s own Status line (both
  still stale as of the same commit) — the discrepancy the user's own
  review instruction named directly; the analogous Phase 62 finding
  (session history, "Check Phase 62 closeout consistency" task, prior to
  this one).
- **classification:** workflow
- **status:** promoted
- **recurrence:** corrected at this triage — see curation note below;
  this is a **first occurrence of this specific shape**, not a second
  occurrence as originally filed.
- **promoted_to:** `planning/agent-led-workflow.md` step 10 (new bullet:
  dispatch `roadmap-context-curator` once more immediately before any
  mid-phase presentation to the actual user/domain owner for approval)
- **curation (Phase 63D triage, 2026-09-23, knowledge-curator):**
  provenance accepted — all required fields present. Independently
  re-verified rather than taking the entry's own account on faith:
  confirmed `planning/ROADMAP.md` row 63D and
  `planning/phase-63d-domain-reconstruction.md`'s own Status line are
  now both correctly "Done 2026-09-23" (commit `507e6f6` applied the
  fix), matching `CONTEXT.md`'s already-correct account — the underlying
  fact of the gap is real and correctly described.

  **Did not take the entry's own "second occurrence (Phase 62)" claim on
  faith — checked it directly, and it does not hold.** Read
  `planning/retros/_audit-phase-62.md` in full: its own item 7
  ("Roadmap/context/changelog/context-gaps/promoted.md") states all of
  `ROADMAP.md`, `v1-redefinition/roadmap.md`, and `CONTEXT.md` were
  "confirmed reflecting actual completion, not aspirational language" by
  the time of that audit — i.e. Phase 62's `ROADMAP.md` row and
  `CONTEXT.md` were never found to disagree, at any point this audit
  could see. Phase 62's own retro (`planning/retros/phase-62-adapter-interface-consolidation.md`)
  independently confirms this: its "Lessons learnt"/"Process-improvement
  feedback" sections are entirely about a *different* issue (a plan's
  own claim about existing adapter code going stale by implementation
  time), and "Process-improvement feedback" explicitly says "None beyond
  the lesson above." The one thing `_audit-phase-62.md` *does* flag as a
  process gap (item 4) is that the audit report itself wasn't written to
  `planning/retros/_audit-phase-N.md` at the time it ran — a report
  *file's own location*, not a planning-status *line's own content*
  disagreeing across files. These are genuinely different failure
  shapes: one is "a deliverable wasn't filed where convention expects
  it," the other is "two files both claim to state the phase's status
  and disagree." **This candidate's own `origin` field already hedges
  this exact point** ("though that specific finding was about a missing
  audit-report file, not this exact pattern") — on inspection, that
  hedge is the correct call, not a minor caveat: Phase 62 is not a
  precedent for this specific shape at all. **Recurrence corrected to:
  first occurrence.**

  This does not make the observation less real or less worth promoting —
  it changes *why* it's promotable. Not "third-strike, mechanically
  overdue" (the original framing), but: a specific, well-evidenced,
  first-occurrence structural gap in `agent-led-workflow.md`'s own
  14-step model, with a concrete, low-cost fix already named by the
  phase's own retro. Checked `.claude/agents/roadmap-context-curator.md`'s
  own Hard rules directly: it *already* mandates reconciling "the
  phase's own `planning/phase-N-*.md` status line" and "`ROADMAP.md`"
  together (`L-006`'s own prior promotion) — so the standing rule this
  gap needed already exists in the agent brief. The actual gap is
  sequencing: `agent-led-workflow.md`'s 14 steps only dispatch
  `roadmap-context-curator` at step 10 (interim, `CONTEXT.md` only, by
  design — `ROADMAP.md` deliberately not flipped yet) and step 14 (final,
  after the retro/triage/audit sequence completes). Phase 63D needed to
  present its work to the actual user/domain owner for approval
  *between* those two points — a case the existing 14 steps don't name a
  checkpoint for — so the existing `roadmap-context-curator` rule never
  got a chance to fire before the user saw the inconsistency. This
  matches the retro's own "Process-improvement feedback" verbatim
  ("Consider whether `roadmap-context-curator`'s own dispatch should
  become a mandatory step immediately before presenting any phase's work
  for user review"). Checked for a merge/duplicate: not a duplicate of
  `L-006`/`L-013` (already-promoted, already-live rules about *what* to
  reconcile) — this is about *when* to reconcile, a distinct, so-far
  unaddressed gap in the step sequence itself. **Outcome: promote**,
  on the strength of specificity + an already-obvious, low-cost fix, not
  recurrence-count (this project's own precedent — `L-006`, `L-018`,
  `L-023` — already promotes well-evidenced first-occurrence workflow
  gaps directly into `agent-led-workflow.md` without waiting for a
  second instance). Classification `workflow` matches this project's own
  established practice of landing such candidates as
  `agent-led-workflow.md` step amendments (not a `.claude/skills/` file,
  despite the lifecycle table's literal "workflow → skill" line — every
  prior `workflow`-classified promotion in `promoted.md` — `L-006`,
  `L-013`, `L-018`, `L-023` — in fact landed in `agent-led-workflow.md`,
  which this triage follows as the controlling precedent). Status left
  as `candidate` (not `promoted`) until the lead actually applies the
  amendment and a `promoted.md` line is added.

  **Recommended amendment — `planning/agent-led-workflow.md`, new
  bullet under step 10 ("Reconcile roadmap and context state
  (interim)")** (draft, for the lead to review and land; not applied
  here):

  > **If this phase's work must be presented to the actual user/domain
  > owner for approval before the phase can be called done** (a
  > Domain-stage corpus, a `design.md` needing sign-off, or any other
  > mid-phase human-decision gate), **dispatch `roadmap-context-curator`
  > once more immediately before that presentation**, not only at step
  > 10's own regular interim point. This pass must cover the same scope
  > as any other reconciliation (the phase's own `planning/phase-N-*.md`
  > Status line and the `ROADMAP.md` row, not `CONTEXT.md` alone) —
  > updating `CONTEXT.md` correctly while leaving `ROADMAP.md`/the plan
  > file's own Status line stale is a real, visible inconsistency a human
  > reviewer will notice before the lead does, confirmed at Phase 63D
  > (`L-034`): `CONTEXT.md` said "corpus complete, awaiting approval"
  > while `ROADMAP.md` and the phase plan still said "not started"/"plan
  > only," caught only by the actual user's own review.

  Revisit/withdraw only if a future phase's own experience shows this
  new checkpoint doesn't actually get triggered reliably (e.g. because
  "must be presented for approval" is itself ambiguous to spot in
  advance), which would argue for a stronger mechanical trigger (a
  `check_user_docs.py` check comparing `CONTEXT.md`'s phase-status
  language against `ROADMAP.md`'s row and the plan file's Status line)
  rather than a prose reminder.

### L-031 — `symbol_enrichment` has no provenance column, unlike its two sibling enrichment tables

- **origin:** Phase 63D (Domain reconstruction), `domain-skeptic`'s own
  independent review of the draft domain corpus, cluster `EVID`'s
  `provenance.md` concept page
- **date:** 2026-09-23
- **project_revision:** `fef153b`
- **observation:** `src/codecompass/graph.py`'s `symbol_enrichment`
  table has exactly four columns (`id`, `symbol_id`, `purpose`,
  `generated_at`) — no `model` column at all, unlike
  `vendor_enrichment`/`doc_relation_enrichment`, which both carry
  `model TEXT NOT NULL`. `decisions/0054`'s own claim that all three
  enrichment tables uniformly distinguish producers "using a column
  that has existed since Phase 14" is factually wrong for
  `symbol_enrichment` specifically — confirmed by reading the real
  schema directly (`graph.py:176-181`) and `graph.record_symbol_enrichment`'s
  own signature (`graph.py:1545-1556`), which has no `model` parameter
  anywhere. `symbol_enrichment` rows currently cannot be attributed to a
  specific producer (agent or automated API call) at all.
- **evidence:** `src/codecompass/graph.py:176-181` (schema),
  `:1545-1556` (`record_symbol_enrichment`);
  `decisions/0054-agent-driven-enrichment-is-a-second-non-authoritative-producer.md`
  (the "uniform column since Phase 14" claim, contradicted for this one
  table); `docs/domain/concepts/provenance.md`'s own counterexample
  section (`OBS-EVID-011`, `CL-EVID-008`), independently re-verified by
  `domain-skeptic` against the real schema
  (`planning/retros/_domain-skeptic-review-phase-63d.md` §3).
- **classification:** future-improvement
- **status:** promoted
- **recurrence:**
- **promoted_to:** `planning/ROADMAP.md` "Future-improvement backlog
  (unscheduled)" section (Phase 63D-Phase 73), then Phase 74's own row
  (`planning/phase-74-provenance-hardening.md`) once actually
  implemented -- landed for real: `symbol_enrichment.model` added via
  `_migrate_symbol_enrichment_model_column`, `record_symbol_enrichment`
  requires a real `model` argument for every new write, its one
  production call site (`enrichment.py:427`) supplies it. Closed
  precisely as this entry's own recommendation named (an additive
  migration, `_migrate_symbols_export_kind_note_columns`'s own pattern),
  with one refinement `domain-skeptic`'s own Phase 74 freshness check
  found: the column is nullable, not `NOT NULL`, since a pre-existing
  row's real producer was never recorded and an honest `NULL` is the
  correct backfill, not a fabricated value.
- **curation (Phase 63D triage, 2026-09-23, knowledge-curator):**
  provenance accepted — all required fields present. Independently
  re-verified rather than taking the candidate's (or `domain-skeptic`'s)
  own account on faith: read `src/codecompass/graph.py:165-203` directly
  and confirmed `symbol_enrichment` (lines 177-182) has exactly four
  columns (`id`, `symbol_id`, `purpose`, `generated_at`) with no `model`
  column, while `vendor_enrichment`/`doc_relation_enrichment` both
  genuinely have `model TEXT NOT NULL`; read
  `graph.record_symbol_enrichment` and confirmed its `INSERT` statement
  and signature have no producer parameter anywhere. Read
  `decisions/0054-agent-driven-enrichment-is-a-second-non-authoritative-producer.md`
  directly and confirmed it does state the "column that has existed
  since Phase 14" claim in a way that reads as applying to "the
  enrichment tables" generally — genuinely stale/inaccurate for
  `symbol_enrichment` specifically, exactly as claimed. Checked for a
  merge/duplicate: grepped `promoted.md`, `ROADMAP.md`, and
  `v1-redefinition/roadmap.md` for "provenance"/"model column"/
  "symbol_enrichment" — no existing roadmap row or promoted learning
  already covers adding provenance attribution to `symbol_enrichment`;
  Phase 57's own Stage E candidate ("graph-level provenance... per-claim
  version + evidence route + confidence state," conditional on GATE DD)
  is a much larger, different-shaped future generalisation that
  `provenance.md`'s own "Relationships" section already correctly
  distinguishes from this narrower, concrete gap — not a duplicate, not
  a reason to fold this into that future work. **Outcome: promote.**
  Classification `future-improvement` correctly maps to a `ROADMAP.md`
  row, finalised by `roadmap-context-curator` (not this role, and not
  landed here — outside both this role's and the lead's usual write
  path for that file). Status left as `candidate` until
  `roadmap-context-curator` actually adds the row and a `promoted.md`
  line is added, per `learning-lifecycle.md` §4/§6. Separately flagging,
  not as part of this promotion: `decisions/0054`'s own "using a column
  that has existed since Phase 14" sentence is now a factually-inaccurate
  standing ADR claim; per `CLAUDE.md` §2, ADRs are append-only, so
  whether this warrants a corrective/errata note is an editorial call
  for whoever owns `decisions/*.md` (the lead), not something this
  future-improvement promotion resolves or should be blocked on.

  **Recommended new `ROADMAP.md` row** (draft, for `roadmap-context-curator`
  to review and land; not applied here):

  > `symbol_enrichment` has no producer-attribution column, unlike
  > `vendor_enrichment`/`doc_relation_enrichment` (both carry `model
  > TEXT NOT NULL`) — `symbol_enrichment` rows currently cannot be
  > attributed to a specific producer (agent or automated API call) at
  > all. Add a `model` column via an additive migration (mirroring
  > `_migrate_symbols_export_kind_note_columns`'s `ADD COLUMN` pattern,
  > Phase 62), or explicitly document the asymmetry as an intentional
  > simplification if a rationale is found. Origin: `L-031` (Phase 63D,
  > `domain-skeptic`'s own review). | FUTURE-IMPROVEMENT | not started | —

### L-032 — the external adapter protocol's wire-level `ecosystem` field and `capabilities` list are received but never validated

- **origin:** Phase 63D (Domain reconstruction), `domain-skeptic`'s own
  independent review of the draft domain corpus, cluster `ADPT`'s
  `ecosystem.md`/`capability.md` concept pages
- **date:** 2026-09-23
- **project_revision:** `fef153b`
- **observation:** `ExternalAdapterProcess.ecosystem`
  (`external_process.py:51,83`) is assigned from an external adapter's
  `initialize` response and never subsequently read, compared against
  `core.Ecosystem`, or used for any dispatch/validation decision
  anywhere in `src/codecompass/adapters/*.py` or `sync.py` — confirmed
  by direct grep of every `.ecosystem` attribute access. Separately,
  `self.capabilities = tuple(response.get("capabilities", []))`
  (`external_process.py:84`) performs no membership check against the
  protocol's own closed 4-value set (`dependencies`/`symbols`/
  `observations`/`diagnostics`) — an adapter reporting a fifth,
  unrecognized capability string would be accepted uncomplainingly.
  Both are real, currently-inert implementation gaps: nothing in the
  current implementation would detect or surface an external adapter
  reporting an `ecosystem` string that disagrees with the `Ecosystem`
  value CodeCompass configured it under, or a bogus capability string.
- **evidence:** `src/codecompass/adapters/external_process.py:51,53-84`
  (both fields, no validation); `docs/domain/concepts/ecosystem.md`'s
  own counterexample section (`OBS-ADPT-017`, `EV-ADPT-010`) and
  `docs/domain/concepts/capability.md`'s own counterexample section
  (`OBS-ADPT-005`), both independently re-verified by `domain-skeptic`
  against the real source
  (`planning/retros/_domain-skeptic-review-phase-63d.md` §3).
- **classification:** future-improvement
- **status:** promoted
- **recurrence:**
- **promoted_to:** `planning/ROADMAP.md` "Future-improvement backlog
  (unscheduled)" section (Phase 63D-Phase 73), then Phase 74's own row
  (`planning/phase-74-provenance-hardening.md`) once actually
  implemented -- landed for real: `ExternalAdapterProcess.initialize`
  now takes a required `expected_ecosystem` argument and validates it
  plus `capabilities` against the closed set, raising `AdapterError` on
  either mismatch. `adapters/haskell.py`'s one production call site
  passes `expected_ecosystem=self.config.ecosystem`. Closed exactly as
  this entry's own recommendation named -- domain-skeptic's own Phase 74
  freshness check confirmed this is a full closure with no residual gap
  (unlike L-031's own narrower nullability caveat).
- **curation (Phase 63D triage, 2026-09-23, knowledge-curator):**
  provenance accepted — all required fields present. Independently
  re-verified rather than taking the candidate's own account on faith:
  grepped `src/codecompass/adapters/external_process.py` and every other
  `.py` file under `src/codecompass/` for `.ecosystem` and `capabilities`
  attribute access — confirmed `self.ecosystem` (line 51, assigned line
  83) is genuinely never read anywhere outside `external_process.py`
  itself (every other `.ecosystem` hit in the codebase belongs to
  `VendorConfig.ecosystem`/`Vendor.ecosystem`, an unrelated, already-used
  field on a different class), and `self.capabilities` (assigned line
  84) is likewise never read or checked against the closed
  `CAPABILITIES = ("dependencies", "symbols", "observations",
  "diagnostics")` tuple defined two lines above it in the same file —
  both fields are write-only within their own class. Confirmed accurate
  exactly as claimed. Checked for a merge/duplicate: grepped
  `promoted.md`/`ROADMAP.md`/`v1-redefinition/roadmap.md` for
  "capabilities"/"validate ecosystem"/"protocol harden" — no existing
  roadmap row or promoted learning already covers validating the
  external-adapter wire protocol's own `ecosystem`/`capabilities`
  fields; distinct from `CG-008` (already resolved, Phase 62 — about
  `symbols` never reaching the graph at all, not about validating these
  two specific handshake fields) and from `decisions/0057`/`0058`/`0059`
  (protocol design ADRs that define the fields but don't validate them
  either). **Outcome: promote.** Classification `future-improvement`
  correctly maps to a `ROADMAP.md` row, finalised by
  `roadmap-context-curator`. Status left as `candidate` until the row is
  actually added and a `promoted.md` line is added, per
  `learning-lifecycle.md` §4/§6. Not merged with `L-031`: both are real
  `src/codecompass/` future-improvement gaps found by the same review,
  but in unrelated subsystems (an enrichment-table schema vs. an
  external-adapter handshake) — a shared origin phase isn't grounds to
  merge two otherwise-independent findings.

  **Recommended new `ROADMAP.md` row** (draft, for `roadmap-context-curator`
  to review and land; not applied here):

  > `ExternalAdapterProcess.initialize()` receives `ecosystem` and
  > `capabilities` from an external adapter's wire response
  > (`external_process.py:83-84`) but never validates either: `ecosystem`
  > is never compared against the `core.Ecosystem` value CodeCompass
  > configured the adapter under, and `capabilities` is never checked
  > against the protocol's own closed 4-value set already defined in the
  > same file (`CAPABILITIES`). An adapter reporting a mismatched
  > `ecosystem` string or an unrecognized capability is currently
  > accepted uncomplainingly. Add a membership/equality check in
  > `initialize()`, raising `AdapterError` on mismatch (matching the
  > existing `protocol_version` mismatch handling immediately above it
  > in the same method). Origin: `L-032` (Phase 63D, `domain-skeptic`'s
  > own review). | FUTURE-IMPROVEMENT | not started | —

### L-030 — a live check's "realness" is not, by itself, evidence that it adds more informative signal than an already-passing fixture suite covering the same surface

- **origin:** Phase 63 (lightweight ordinary-project smoke test), retro
  "Lessons learnt" (the retro explicitly declined to file this as an
  `L-NNN`, reasoning it "doesn't generalise past 'read what a partial
  live check would and wouldn't cover before assuming it's worth
  running,' which is already this project's own standing evidence-first
  discipline, not a new rule"); filed at this triage's own initiative,
  dispatched specifically because a `release-phase-auditor` DoD audit of
  Phase 63 flagged the retro's own non-filing decision as itself a
  curation judgment `CLAUDE.md` §8 reserves for `knowledge-curator`, not
  something the implementing lead should resolve unilaterally — the same
  pattern flagged, and then fixed, during Phase 62's own closeout audit
  (`planning/retros/_audit-phase-62.md`, resulting `L-029`, merged into
  `L-014`).
- **date:** 2026-09-22
- **project_revision:** `6298154` (Phase 63's own closeout commit)
- **observation:** the plan originally scoped a live clone of an
  ordinary npm project (Technical Clipper) to smoke-test whether Phases
  60-62's shared adapter-wiring changes (`EcosystemAdapter.symbols()`,
  `sync.py`'s `_collect_vendor_symbols` removal) disturbed ordinary
  npm/Python/Cargo project support. Amended before implementation once
  `which npm`/`which cargo` both confirmed absent from the sandbox: the
  live clone was dropped entirely rather than run partially, because a
  live bootstrap could only exercise `NpmAdapter.installed_version()`/
  `source_location()`/`readme_and_api_surface()` — never
  `dependency_tree()`, the one method requiring a real `npm ls`
  subprocess call and the one method closest to what Phases 60-62's
  `sync.py` wiring changes could plausibly have disturbed. Independently
  re-confirmed directly against `src/codecompass/adapters/npm.py`:
  `dependency_tree()` (line 41) is the only one of the four methods that
  shells out to `npm ls`; the other three read `node_modules/<name>/
  package.json` and on-disk files directly, no subprocess involved. The
  full regression suite (`pytest`: 623 passed, 2 skipped — identical to
  Phase 62's own closeout baseline) was judged to give more actual
  coverage of the changed surface than the partial live run would have,
  and was used as this phase's entire evidence base instead. Generalised
  statement: "live/real" and "more informative" are different axes — a
  check's evidentiary value depends on what fraction of the actually-
  changed surface it exercises, not on whether it runs against a real
  external project versus a fixture.
- **evidence:** `planning/phase-63-lightweight-smoke-test.md` §1-2
  ("Design decisions": "A live bootstrap that can only exercise three of
  `NpmAdapter`'s five methods... risks *looking* like a real regression
  check while actually testing less than the existing fixture suite
  already does"); `planning/retros/phase-63-lightweight-smoke-test.md`
  "Scope delivered vs planned" + "Lessons learnt";
  `src/codecompass/adapters/npm.py` lines 17, 20, 41, 58 (read directly
  at this triage — confirmed `dependency_tree()` is the sole
  subprocess-`npm ls`-dependent method among the four); Phase 62's own
  closeout baseline (`planning/retros/_audit-phase-62.md`: "623 passed, 2
  skipped") cross-checked against Phase 63's own re-run of the identical
  numbers.
- **classification:** scoped-rule
- **status:** discarded
- **recurrence:** none yet — first filed occurrence of this specific
  reasoning. If a future phase again treats "runs against a real
  external project" as self-evidently stronger evidence than an
  already-passing, more complete fixture/regression suite — without
  first checking what fraction of the actually-changed surface the live
  run would exercise — that would be a second occurrence, and this
  entry's `discarded` status should be revisited toward `retained` or
  `promoted`.
- **curation (Phase 63 triage, 2026-09-22, knowledge-curator):**
  provenance accepted — assigned this id, all required fields now
  present. Independently re-derived the central claim rather than taking
  the retro's own account on faith: read
  `planning/phase-63-lightweight-smoke-test.md` and
  `planning/retros/phase-63-lightweight-smoke-test.md` directly, then
  independently read `src/codecompass/adapters/npm.py` and confirmed
  `dependency_tree()` (line 41) is genuinely the only one of the four
  cited methods that calls `npm ls` via subprocess — the other three
  (`installed_version`, `source_location`, `readme_and_api_surface`,
  lines 17/20/58) read on-disk files directly, exactly as the plan and
  retro both claim. Checked for a merge/duplicate candidate first, per
  this queue's own established practice: distinct from `L-017` (live
  `WebFetch` of an external reference manual — an expense/reliability
  axis, not a coverage-completeness axis) and from `L-020`
  (content-hash pinning proves an excerpt hasn't changed, not that its
  boundary is complete — an excerpt-fidelity axis, not a test-design
  axis); no existing candidate covers "live execution against a real
  external project is not automatically stronger evidence than an
  already-passing, more complete fixture suite," so this is a genuine
  first occurrence, not a merge target.

  Considered the retro's own "doesn't generalise past... this project's
  own standing evidence-first discipline" reasoning on its merits rather
  than deferring to it, exactly as `L-029`'s own triage did for the
  equivalent Phase 62 finding: agreed that, framed at that level of
  generality, this is not a newly-discovered failure mode, but
  disagreed that this makes the observation not candidate-worthy in the
  first place — `CLAUDE.md` §8 is explicit that "the lead deciding
  unilaterally that something isn't candidate-worthy" is not itself how
  this project resolves that question; only `knowledge-curator`'s own
  triage is. On the substance: this is the same shape `L-014` (Phase 44,
  status: discarded) already established — a single-occurrence,
  zero-harm instance of an *already-existing* project discipline
  (`agent-led-workflow.md` line 10's "verify independently, every time,"
  and `CLAUDE.md` §1's plan-then-pause-then-implement sequence) working
  exactly as intended, not an unaddressed gap needing a new mechanism.
  The plan's own §1/§2 "Design decisions" already did the weighing this
  observation describes — named which specific method
  (`dependency_tree()`) the live check would and wouldn't reach, compared
  that against the unchanged 623-passed fixture baseline, and chose
  accordingly, with the user's explicit sign-off per `CLAUDE.md` §1's
  pause-and-ask requirement once the plan surfaced the open choice.
  Nothing broke, no wrong verification method was chosen, and no
  standing content was left wrong the way `L-004`/`L-003` describe (the
  distinguishing test `L-014`'s own curation note applies). **Outcome:
  discard, not retain or promote.** This is not a rubber-stamp of the
  lead's original non-filing call: the *substantive* conclusion (this
  doesn't yet warrant a new standing rule) happens to match the lead's
  own, but it is now reached via the process `CLAUDE.md` §8 actually
  requires — an explicit `knowledge-curator` judgment, filed, evidenced,
  and checked against the two directly-relevant precedents (`L-014`,
  `L-017`/`L-020` as near-miss non-matches) — rather than the
  implementing agent's own say-so, closing exactly the gap the
  `release-phase-auditor` flagged. A second occurrence of this specific
  reasoning (treating "live" as self-evidently better evidence without
  checking actual coverage) would be the trigger to revisit this
  `discarded` status rather than filing a fourth independent entry.
- **promoted_to:** — (discarded; see rationale above)

### L-029 — a plan's own claim that several files already duplicate a piece of logic should be re-verified against each real file at implementation time before executing the plan's literal per-file refactor prescription

- **origin:** Phase 62 (adapter-interface consolidation), retro "What
  didn't work" + "Lessons learnt" + "Candidate learnings filed" (the
  retro explicitly declined to file this as an `L-NNN`, reasoning it
  "doesn't generalize past 'read the code you're about to change,'...
  not a new rule"); filed at this triage's own initiative, dispatched
  specifically because a `release-phase-auditor` DoD audit of Phase 62
  flagged the retro's own non-filing decision as itself a curation
  judgment `CLAUDE.md` §8 reserves for `knowledge-curator`, not
  something the implementing lead should resolve unilaterally — every
  other recently-audited phase (49, 53, 43b, 42, 60) dispatched
  `knowledge-curator` even when the eventual disposition was "nothing
  new."
- **date:** 2026-09-19
- **project_revision:** `96428a8` (Phase 62's own implementation
  closeout commit)
- **observation:** `planning/phase-62-adapter-interface-consolidation.md`'s
  own design section described refactoring each of
  `NpmAdapter`/`PythonAdapter`/`CargoAdapter`'s own
  `readme_and_api_surface()` to call a new `self.symbols()` method,
  premised on a planning-time claim that all three adapters already
  duplicated a per-file walk+extract loop inside their own
  `readme_and_api_surface()`. This was true for `CargoAdapter`/
  `PythonAdapter` but factually wrong for `NpmAdapter` — independently
  re-confirmed by reading `src/codecompass/adapters/npm.py`'s current
  `readme_and_api_surface()` (lines 58-66) directly: it globs `README*`
  and `*.d.ts` files and dumps their raw text; it never calls
  `extract_npm_symbols` or performs any per-file symbol extraction. The
  lead caught this only by reading all three adapter files closely again
  at implementation time (not trusting the plan's own summary of "what
  the three adapters do"), and adjusted the design to a base-class
  concrete default (`EcosystemAdapter.symbols()`, confirmed live at
  `src/codecompass/adapters/base.py` lines 72-96, using
  `iter_source_files`/`extract_symbols_for_file`) rather than executing
  the plan's literal per-adapter refactor. The retro itself further notes
  that following the plan's literal prescription for Cargo/Python would
  *also* have silently changed their rendered `readme_and_api_surface()`
  output (losing per-file grouping headers, since `Symbol` carries no
  file-path field) — a real, avoidable regression the base-class-default
  design sidesteps entirely, not a purely cosmetic difference from what
  was planned.
- **evidence:**
  `planning/retros/phase-62-adapter-interface-consolidation.md` "What
  didn't work" + "Lessons learnt" (both independently re-read, not taken
  on the retro's own summary alone);
  `src/codecompass/adapters/npm.py::NpmAdapter.readme_and_api_surface`
  (lines 58-66, read directly at this triage — confirmed it never calls
  `extract_npm_symbols`); `src/codecompass/adapters/base.py::EcosystemAdapter.symbols`
  (lines 72-96, read directly at this triage — confirmed it is the new
  concrete base-class default the retro describes).
- **classification:** scoped-rule
- **status:** merged:L-014
- **recurrence:** second occurrence of the same underlying pattern
  L-014 (Phase 44) already covers — a plan's own claim about current
  code state (there, which agent briefs still had placeholder sections;
  here, which adapters duplicated a walk+extract loop) turns out partly
  stale/wrong by implementation time, and this project's own standing
  practice (`CLAUDE.md` §1's planning discipline plus
  `agent-led-workflow.md`'s "verify independently, every time" opening
  line, both already cited in L-014's own curation note) catches it
  before any wrong artifact ships.
- **curation (Phase 62 triage, 2026-09-19, knowledge-curator):**
  provenance accepted — assigned this id, all required fields now
  present. Independently re-derived the central claim rather than taking
  the retro's own account on faith: read
  `planning/retros/phase-62-adapter-interface-consolidation.md`'s "What
  didn't work"/"Lessons learnt" sections directly, then independently
  read `src/codecompass/adapters/npm.py` (confirmed `readme_and_api_surface`
  never touches `extract_npm_symbols`) and `src/codecompass/adapters/base.py`
  (confirmed `EcosystemAdapter.symbols()` is a real, concrete, already-
  landed base-class default at the exact call sites the retro names) —
  both hold exactly as described, not merely as claimed. Considered the
  retro's own "doesn't generalize past 'read the code you're about to
  change'" reasoning on its merits rather than deferring to it: agreed
  that framed at that level of generality this is not a new rule, but
  disagreed that this makes the observation not candidate-worthy —
  `CLAUDE.md` §8 is explicit that "the lead deciding unilaterally that
  something isn't candidate-worthy" is not itself how this project
  resolves that question; only `knowledge-curator`'s own triage is.
  Checked for a merge/duplicate candidate first, per this queue's own
  established practice: **this is the same shape L-014 (Phase 44,
  status: discarded) already triaged** — a plan document's own factual
  claim about current code state (not its scope list) goes stale/wrong
  between writing and implementation, caught by this project's already-
  standing "read the code, verify independently" discipline before any
  wrong artifact shipped, with zero resulting harm. L-014's own curation
  note explicitly reserved exactly this scenario for future handling:
  "If a future phase's *background claim* being stale actually causes a
  wrong edit (not just a wasted-but-caught assumption), that would be a
  new, stronger candidate — not a recurrence of this one, since this one
  caused no harm." Applying that test here: Phase 62's stale claim was
  caught *before* any `npm.py`/`cargo.py`/`python.py` edit was made (the
  retro's own "Scope delivered vs planned" states "zero changes to
  `adapters/npm.py`/`cargo.py`/`python.py`") — this is a "wasted-but-
  caught assumption" exactly like L-014's instance, not the "actually
  caused a wrong edit" case L-014 reserved for a stronger, independently-
  promotable candidate. The regression risk the retro flags (losing
  per-file grouping headers for Cargo/Python) was avoided by the design
  change, not realized — a near-miss on top of a near-miss, not an actual
  incident. **Outcome: merge into L-014, not a fresh discard and not a
  promotion.** This is not the same as rubber-stamping the lead's
  original non-filing call: the *substantive* conclusion (this doesn't
  yet warrant a new standing rule) happens to match the lead's own, but
  it is now reached via the process `CLAUDE.md` §8 actually requires —
  an explicit `knowledge-curator` judgment, filed, evidenced, and
  checked against the one directly-relevant precedent — rather than the
  implementing agent's own say-so, closing exactly the gap the
  `release-phase-auditor` flagged. Recorded here as a second occurrence
  so recurrence counts aggregate on `L-014` correctly, per
  `learning-lifecycle.md` §4's `merge` semantics: a *third* occurrence,
  or one that actually reaches production (a wrong edit, not just a
  wrong plan sentence), would be the trigger to revisit L-014's own
  discarded status rather than adding a fourth independent entry.
- **promoted_to:** — (merged into L-014; not independently promoted —
  see curation note)

### L-028 — `resolve_and_clone`'s `subdirectory` field scopes the *rendered* view of a monorepo member, not the raw on-disk clone itself — a documentation gap, not a new bug

- **origin:** Phase 61 (hledger cross-language experiment),
  `reference-project-tester`'s own `OBS-015`
  (`planning/context-observations/inbox.md`)
- **date:** 2026-09-19
- **project_revision:** `9f8b510` (the Phase 61
  `HaskellAdapter.repository_url()` fix commit)
- **observation:** Phase 61's own plan (`planning/phase-61-hledger-cross-language-experiment.md`,
  §"Verification") stated the §4 fix would make
  "`vendor/hledger-lib/src/` now contain only `hledger-lib`'s own real
  files... no `hledger`/`hledger-ui`/`hledger-web` siblings." This is
  **not what `resolve_and_clone` does, and never has been** — confirmed
  by reading `source_resolution.py::resolve_and_clone`'s own docstring
  directly: it clones the *whole* upstream repository into `dest`
  unconditionally, and `subdirectory` only ever changes what
  `tree_root` (the value it *returns*) points at — the raw `dest`
  directory is never pruned, for any ecosystem, including npm's own
  pre-existing monorepo case (`decisions/0021`). The plan's own
  Verification wording overclaimed what the real, pre-existing mechanism
  produces; the actually-correct, actually-fixed consumers are
  `FILETREE.md`/the symbol index/`tree_root`-based rendering (confirmed
  working, `reference-project-tester` found zero cross-contamination
  there) — the raw on-disk `vendor/<name>/src/` clone being the whole
  repo is expected, unrelated to this fix, and (for two siblings sharing
  one URL) doubles real disk usage (136M × 2 in this real instance) — a
  cost already disclosed and accepted in the plan's own review gate, but
  not connected there to *this* specific symptom.
- **evidence:** `planning/context-observations/inbox.md` `OBS-015`;
  `src/codecompass/source_resolution.py::resolve_and_clone`'s own
  docstring ("Returns the resolved source root within the clone — `dest`
  itself, or `dest / subdirectory`...").
- **classification:** architecture
- **status:** promoted (landed by the lead, 2026-09-19).
- **recurrence:** first occurrence as filed; the underlying mechanism
  (`resolve_and_clone` never pruning `dest`) is pre-existing since Phase
  7 (`decisions/0021`) and applies identically to npm's own monorepo
  case — Phase 61 is simply the first real scenario to place two
  siblings sharing one repository URL side by side, making the
  duplication/cross-contamination directly observable for the first
  time (`OBS-015`'s own root-cause trace, independently re-read).
- **curation (Phase 61 triage, 2026-09-19, knowledge-curator):**
  provenance accepted — all required fields present. Independently
  re-verified rather than taking the entry's own account on faith: read
  `src/codecompass/source_resolution.py::resolve_and_clone` directly and
  confirmed its own docstring states the function returns `dest` or
  `dest / subdirectory` as `source_root`, with no code path anywhere in
  the function pruning, moving, or restricting what physically lands at
  `dest` — the raw clone genuinely is always the whole upstream
  repository, exactly as `OBS-015` traced. Cross-checked
  `architecture/overview.md`'s current `RepositoryLocation(url,
  subdirectory)` bullet (the closest existing description of this
  mechanism) and confirmed it says nothing about which artifact
  `subdirectory` scopes (rendered view vs. raw clone) — a real, present
  gap this candidate's own "documentation gap, not a new bug" framing
  correctly diagnoses; the "Known footguns" section already documents
  the adjacent, but distinct, `vendor/<name>/src/` gitignore-and-
  regenerate behavior (`decisions/0010`) without ever addressing
  monorepo-sibling duplication, so this is a genuine gap in that
  section, not a restatement of an existing bullet. Checked for a
  merge/duplicate: this is the direct generalization of `OBS-015`
  (already correctly filed as a context-observation, not a
  context-gap, per that entry's own reasoning — "an implementation gap
  in one function's own behaviour," not a missing graph relationship) —
  `L-028` is this triage's own extraction of the generalizable lesson
  from that instance, not a separate finding requiring independent
  verification of the underlying mechanism. **Outcome: promote.**
  Classification `architecture` (description of current architecture)
  maps to an `architecture/` doc, finalised by `docs-maintainer`, per
  `learning-lifecycle.md` §4 — reclassifying from a bug-shaped read to a
  documentation-shaped one is correct here: nothing about
  `resolve_and_clone`'s behavior is wrong or needs code changed (the
  npm monorepo case has worked this way since Phase 7 without incident);
  what's missing is a sentence stating what `subdirectory` actually
  scopes, so a future reader (agent or human) doesn't repeat this same
  plan-verification overclaim. Destination:
  `architecture/overview.md`'s "Known footguns" section (not
  `docs/external-adapters.md`, which contains no `subdirectory`/
  monorepo content to attach this to, confirmed by grep — zero matches).

  **Recommended fix — new bullet in `architecture/overview.md`'s "Known
  footguns" section** (draft, for `docs-maintainer`/the lead to review
  and land; not applied here):

  > **`resolve_and_clone`'s `subdirectory` scopes the *rendered* view
  > only, never the raw on-disk clone.** `_git_clone` always clones the
  > *whole* upstream repository into `dest` (`vendor/<name>/src`);
  > `subdirectory` only changes the function's *return value*
  > (`source_root = dest / subdirectory`), which `sync_vendor` consumes
  > as `tree_root` for rendering `FILETREE.md`/the symbol index. For a
  > monorepo (npm's `repository.directory`, or two Haskell packages
  > sharing one repository URL — Phase 61), every vendor backed by the
  > same upstream repository gets its own full, duplicate, unscoped
  > clone at `vendor/<name>/src/` — doubled disk cost per sibling, and a
  > real misattribution risk for anyone who `grep`s/`find`s the raw
  > clone directly instead of following `FILETREE.md`. Confirmed live at
  > Phase 61 (`OBS-015`): `vendor/hledger-lib/src/` and
  > `vendor/hledger/src/` are byte-identical top-level listings of the
  > whole monorepo, while both packages' `FILETREE.md`s stay correctly
  > scoped to their own package.

  Revisit/withdraw only if a future phase actually prunes `dest` to
  `subdirectory` (at which point this bullet describes stale behavior
  and should be removed, not merely amended) — not expected to be
  contested on the facts, since both this candidate and `OBS-015`
  independently re-derived the same mechanism directly from source.
- **promoted_to:** `architecture/overview.md`'s "Known footguns" section
  (landed by the lead, 2026-09-19).

### L-027 — a single-trial baseline/treatment agent comparison cannot cleanly separate "the tool's contribution" from "agent diligence variance"

- **origin:** Phase 61 (hledger cross-language experiment),
  `context-evaluator`'s own independent evaluation
  (`planning/reference-projects/ledgerkit/03-hledger-cross-language-evaluation.md`)
- **date:** 2026-09-19
- **project_revision:** working tree (Phase 61 implementation,
  uncommitted at filing time)
- **observation:** Phase 61's Part 2 (cross-language equivalence
  recognition) produced a materially better treatment report than
  baseline — treatment found a real, previously-unrecorded divergence
  (Ledgerkit's `stats()` under-excludes commodities under a depth limit,
  independently confirmed live by `context-evaluator` against the real
  pinned `hledger` binary and Ledgerkit's own CLI) that baseline missed
  entirely. On its face this looks like CodeCompass helping. It isn't:
  both agents' own file-read logs show they read the *exact same*
  decisive raw source (`Stats.hs`, the same `reports.py` lines) — the
  divergence is not tracked as a CodeCompass vendor at all (Ledgerkit's
  own source has no generated digest in play), so both conditions had
  byte-identical access to the evidence that actually revealed it. One
  agent simply read more carefully than the other. Attributing this
  quality delta to CodeCompass would have been a real, if easy,
  evaluation error — the instrument's own report structure doesn't
  automatically flag single-agent-diligence confounds in a two-run,
  N=1-per-condition design.
- **evidence:**
  `planning/reference-projects/ledgerkit/03-hledger-cross-language-evaluation.md`
  §"Part 2 context advantage" and §"Material gaps / failures" (the
  "[Methodology]" bullet).
- **classification:** workflow
- **status:** promoted (landed by the lead, 2026-09-19).
- **recurrence:** first occurrence
- **curation (Phase 61 triage, 2026-09-19, knowledge-curator):**
  provenance accepted — all required fields present. Independently
  re-read
  `planning/reference-projects/ledgerkit/03-hledger-cross-language-evaluation.md`
  §"Part 2 context advantage" and the "[Methodology]" bullet under
  "Material gaps / failures" directly rather than trusting the
  candidate's own summary — confirmed both agents' file-read logs are
  cited as showing identical access to `Stats.hs`/the decisive
  `reports.py` lines, and confirmed the report frames this explicitly as
  a methodology caveat `context-evaluator` itself surfaced, not
  something this triage is inferring after the fact. This is a real,
  specific, well-evidenced observation about the shared evaluation
  instrument's own blind spot (a two-run, N=1-per-condition design has
  no structural way to distinguish "the tool helped" from "one agent
  read more carefully"), not a one-off. Checked for a merge/duplicate:
  grepped this inbox for "single-trial"/"N=1"/"diligence" — no prior
  candidate names this confound; distinct from `L-020` (an extraction-
  boundary defect within one artifact, not an evaluation-design
  confound) and from every `OBS-*` entry in the sibling
  context-observations queue (those record *edge*-level experience, not
  the shared *instrument's* own methodological gap). Checked whether
  `planning/v1-redefinition/context-quality-evaluation.md` has ever been
  edited directly by a prior `knowledge-curator` curation (as opposed to
  amended by whoever ran the phase) before treating it as within reach:
  grepped `promoted.md` and this inbox for the file's own name — zero
  `promoted_to` pointers into it, and its own in-file "Amended
  2026-09-12"/"Amended again 2026-09-17"/"Amended again 2026-09-18"
  notes each read as the *phase's own* addition (Phase 54b's "execution-
  path completeness" criterion, credited to that phase's plan
  directly), not as a `knowledge-curator` triage outcome — no precedent
  establishing this file is within this role's own write boundary, and
  it is not one of the four directories this role's hard rules name as
  writable. Per this task's own explicit instruction to treat this as an
  unresolved boundary question rather than deciding it unilaterally:
  **not editing the file** — recommending only. **Outcome: promote
  (recommendation + draft; does not land here).** Destination:
  `context-quality-evaluation.md`, following the exact precedent Phase
  54b's own "execution-path completeness" addition set (a phase-driven
  amendment to the shared instrument, landed by whoever runs the phase,
  not by this role) — not `agent-led-workflow.md` (this is about what
  the *evaluation instrument itself* must check, not agent-dispatch
  procedure) and not a `.claude/` skill/rule (the classification-table's
  literal "scoped rule → `.claude/` config" mapping doesn't fit a
  methodological caution embedded in a shared spec document, the same
  reasoning `L-022`'s curation used to land its own fix in
  `reference-project-protocol.md` instead of a skill file).

  **Recommended addition — `context-quality-evaluation.md` §1 (Ground
  rules) or a new "Amended" note** (draft, for the lead to review and
  land; not applied here):

  > **Amended 2026-09-19** (Phase 61 — `L-027`): a single-trial (N=1-per-
  > condition) baseline/treatment comparison cannot, by construction,
  > separate "the tool's real contribution" from "one agent read more
  > carefully than the other." Before crediting CodeCompass for a
  > treatment-arm finding the baseline missed, explicitly check whether
  > both arms had equal raw-source access to the decisive evidence (both
  > agents' own file-read logs, not just the polish of the final
  > report) — if they did, the quality delta is agent-diligence
  > variance, not a context-quality result, regardless of how well the
  > treatment report reads. Confirmed necessary at Phase 61: Part 2's
  > real, independently-confirmed divergence discovery would have been
  > misattributed to CodeCompass had `context-evaluator` not made this
  > check explicitly (both agents had read the exact same decisive raw
  > source, which was not itself a CodeCompass vendor).

  Scoped to the specific confound this incident evidences (equal
  raw-source access, unequal report quality), not a broader
  "distrust every treatment result" restatement. Revisit/withdraw if the
  lead judges §1's existing ground rules (particularly "a technically-
  correct result that offers little advantage... is recorded honestly as
  low-advantage") already close enough to this concern once pointed out,
  or if the file is confirmed to be within a future `knowledge-curator`
  dispatch's own write boundary, in which case land it directly rather
  than re-drafting.
- **promoted_to:** `planning/v1-redefinition/context-quality-evaluation.md`
  §1 (landed by the lead, 2026-09-19) — write-boundary question resolved
  in the lead's own favour for this file (matches the file's own
  established convention of phase-driven "Amended" notes).

### L-026 — an ecosystem adapter's generated API-surface digest answers "what exists and what's it called," not "what does it do" — a structural limit, not a per-instance gap

- **origin:** Phase 61 (hledger cross-language experiment),
  `context-evaluator`'s own independent evaluation and
  `reference-project-tester`'s own `OBS-016`
  (`planning/context-observations/inbox.md`)
- **date:** 2026-09-19
- **project_revision:** working tree (Phase 61 implementation,
  uncommitted at filing time)
- **observation:** the real, adapter-generated `vendor/hledger/CLAUDE.md`
  (rendered from `readme_and_api_surface()`, already proven correct in
  Phase 60) contains zero "depth"-related content anywhere across 44
  rendered command modules, including the `Stats`/`Balance`/`Register`/
  `Accounts`/`Print` entries the Phase 61 task specifically asked about
  — each renders as a bare `name: one-line purpose` pair with no
  control-flow or business-logic detail. `context-evaluator` confirmed
  this is not a treatment-agent failure to look hard enough
  (`grep -ci depth` on the file genuinely returns `0`) but a real,
  structural property of what `readme_and_api_surface()` extracts for
  *any* ecosystem — a symbol's own one-line doc comment, never its
  body. `reference-project-tester`'s own `OBS-016` recorded the same
  finding independently, framed as "recurs the same structural limit
  `OBS-014` (Phase 54b) already recorded for the curated-corpus
  condition, now reconfirmed against the live adapter-derived digest" —
  i.e. this is the *third* independent occurrence of the same underlying
  limit (curated docs, then live Haskell adapter output), not a one-off.
- **evidence:**
  `planning/reference-projects/ledgerkit/03-hledger-cross-language-evaluation.md`
  §"Material gaps / failures"; `planning/context-observations/inbox.md`
  `OBS-016`; `planning/context-gaps/inbox.md`'s prior `OBS-014` (Phase
  54b).
- **classification:** invariant (filed) — reclassified to **architecture**
  at this triage (see curation note)
- **status:** promoted (landed by the lead, 2026-09-19).
- **recurrence:** third occurrence (curated `dev-docs/hledger-reference/`
  content, Phase 54b, `OBS-014`; live Haskell adapter output, Phase 61,
  `OBS-016` + this evaluation) — a real candidate for promotion.
- **curation (Phase 61 triage, 2026-09-19, knowledge-curator):**
  provenance accepted — all required fields present. Independently
  re-verified rather than taking the entry's own account on faith: read
  `planning/reference-projects/ledgerkit/03-hledger-cross-language-evaluation.md`'s
  §"Material gaps / failures" directly and confirmed it states `grep -ci
  depth vendor/hledger/CLAUDE.md` returns `0`; independently re-read
  `OBS-016` and `OBS-014` in full rather than trusting this candidate's
  paraphrase of either — both confirm the same shape (a symbol's
  one-line declared purpose, never its body) via two structurally
  different mechanisms (a hand-curated `.md` corpus at Phase 54b, a
  live adapter-generated Haddock digest at Phase 61). Considered the
  candidate's own explicit question — does the ≥2-occurrence bar this
  project uses for `context-gaps/` promotion transfer to a *learning*
  candidate — and judges yes, by analogy rather than by rule: the
  `learning-lifecycle.md` §2 "candidate → evidence" step already treats
  recurrence as exactly this kind of promotion signal ("it recurs, or a
  second agent hits it... knowledge curation" following), and three
  independent occurrences across two structurally different context
  sources (curation-time human selection vs. mechanical live
  generation) is stronger evidence of a structural, non-incidental limit
  than either `OBS-014` or `OBS-016` had alone — each of which correctly
  declined escalation on its own (a single instance is not yet a
  pattern). **Reclassifying `invariant` → `architecture`**: this is not
  a behavioral invariant a regression test could usefully encode (there
  is no bug — `readme_and_api_surface()` extracting only declared
  one-line purposes is working exactly as designed for every ecosystem,
  confirmed by direct code reading of the Haddock-extraction path this
  same phase already exercised for L-028/`OBS-015`'s adjacent finding);
  it is a real, current, general property of the adapter architecture
  that is not yet written down anywhere a future phase-planner would see
  it before re-discovering it a fourth time. `architecture` classifi-
  cation correctly maps to an `architecture/` doc (`learning-lifecycle.md`
  §4), finalised by `docs-maintainer`. Checked for a merge/duplicate:
  not a duplicate of `OBS-014`/`OBS-016` themselves (this candidate is
  their generalization into a durable artifact, which is exactly what a
  `planning/learnings/` candidate is for once a context-observation
  recurs enough to justify one — matching the "an investigation
  converges on... `detector_gap`/`graph_capability_gap` → file or link a
  context-gaps entry" pattern this role's own charter describes for the
  sibling queue, applied here to the learnings queue instead since
  nothing about this finding is a missing graph relationship or a
  detector defect). **Outcome: promote.** Destination:
  `architecture/overview.md`'s "Known footguns" section, alongside the
  existing per-ecosystem API-surface footguns already there (the npm
  `.d.ts` cap, the Cargo line-based-scan miss) — this bullet documents a
  cross-ecosystem structural ceiling common to all of them, not a
  per-ecosystem quirk, so it belongs as its own bullet rather than
  amending any single ecosystem's existing one.

  **Recommended fix — new bullet in `architecture/overview.md`'s "Known
  footguns" section** (draft, for `docs-maintainer`/the lead to review
  and land; not applied here):

  > **`readme_and_api_surface()` (any ecosystem adapter) extracts a
  > symbol's declared one-line purpose (doc-comment/docstring/Haddock),
  > never its body.** It answers "what exists and what's it called," not
  > "what does it do" or "why does behaviour differ between two call
  > sites of it." Confirmed three times independently across two
  > structurally different context sources: a hand-curated
  > `dev-docs/hledger-reference/` corpus (Phase 54b) and a live
  > Haskell-adapter-generated `CLAUDE.md` digest (Phase 61 — `grep -ci
  > depth` returns `0` across all 44 rendered command modules, including
  > the ones the task specifically asked about). A task whose answer
  > depends on control-flow/business-logic detail inside a function body
  > is not answerable from the digest alone, regardless of ecosystem or
  > whether the digest came from human curation or mechanical
  > generation — direct source reading is required for that class of
  > question by design, not by omission.

  Revisit/withdraw only if a future phase adds real body-level
  extraction (e.g. a summarization pass over function bodies) to
  `readme_and_api_surface()`, at which point this bullet would need
  removing or narrowing, not merely amending.
- **promoted_to:** `architecture/overview.md`'s "Known footguns" section
  (landed by the lead, 2026-09-19).

### L-025 — a monorepo-aware Stack command needs an explicit `TARGET` argument, or it silently reports the whole project's graph instead of one package's own closure

- **origin:** Phase 60 (minimal external Haskell adapter), discovered
  live while implementing `Adapter.Deps` (checked directly against the
  real `hledger`/`hledger-lib` monorepo, not assumed)
- **date:** 2026-09-19
- **project_revision:** working tree (Phase 60 implementation,
  uncommitted at filing time)
- **observation:** `decisions/0057`'s own original inline description of
  `stack dot --external`/`stack ls dependencies` (and this phase's own
  early plan text) named the bare commands with no target. Run bare
  (`stack dot --external`, no package name) inside `hledger-lib/`, both
  commands report the **whole enclosing multi-package Stack project's**
  dependency graph (all of `hledger`/`hledger-lib`/`hledger-ui`/
  `hledger-web`'s combined closure) — real, live output confirmed
  `hledger`'s own edges appear in the result even when only `hledger-lib`
  was wanted. Passing the package name as an explicit positional
  `TARGET` argument (`stack dot --external hledger-lib`, `stack ls
  dependencies --external hledger-lib`) correctly scopes both commands to
  exactly that one package's own dependency closure — confirmed by a real
  edge-count diff (594 lines vs. 2046 lines for the bare form; zero
  `"hledger" ->` edges in the scoped output vs. 42 in the unscoped one).
- **evidence:** live shell transcript (`stack dot --external
  hledger-lib` vs. bare `stack dot --external`, both run inside
  `/home/cormac/projects/hledger/hledger-lib`), `stack dot --help`/`stack
  ls dependencies --help`'s own documented `TARGET` argument ("If none
  specified, use all project packages").
- **classification:** invariant
- **status:** retained
- **recurrence:** first occurrence
- **curation (Phase 60 triage, 2026-09-19, knowledge-curator):** provenance
  accepted — all required fields present. Independently re-verified rather
  than taking the entry's own account on faith: read
  `adapters/haskell/src/Adapter/Deps.hs` directly (a separate repository,
  checked out at `adapters/haskell/`) and confirmed both `stack`
  invocations already hardcode `packageName` as the explicit positional
  `TARGET` — `runStack projectRoot ["dot", "--external", packageName]`
  (line 43) and `runStack projectRoot ["ls", "dependencies", "--external",
  packageName]` (line 47) — so the fix this candidate names is genuinely
  live, not merely claimed. Also confirmed the module's own header haddock
  comment (lines 4-12) already states the exact invariant this candidate
  documents, in matching detail and almost matching wording ("without it,
  a package inside a multi-package Stack project (a monorepo like
  `hledger`) reports the *whole project's* dependency graph, not the one
  target package's own closure (confirmed live against the real
  `hledger`/`hledger-lib` checkout)") — the invariant already has a
  durable, correctly-scoped home at the exact file whose logic it governs,
  written before this triage touched it. Checked `decisions/0057` directly
  for overlap: its own "Monorepo package roots" section documents a
  related but distinct concern — which *directory* CodeCompass resolves
  and hands to the adapter as `project_root` before invocation — and says
  nothing about the `TARGET` argument `stack dot`/`stack ls dependencies`
  themselves require once already inside that directory; not a duplicate,
  and not a gap this ADR needs amending to close, since the ADR's own
  scope (protocol-level `project_root` resolution) never claimed to cover
  a downstream command's own argument requirements. Checked
  `adapters/haskell/test/Spec.hs`: it exercises `buildTreeFromOutputs`
  (the pure parsing core) against recorded real-shaped text, matching
  `decisions/0014`'s fixture-based-primary-strategy precedent applied on
  the Haskell side — it does not, and structurally cannot without a live
  `stack` subprocess against a real multi-package monorepo, exercise
  `runStack`'s own argument construction. Considered whether classification
  `invariant`'s standard destination (a regression test, per
  `learning-lifecycle.md` §4) still applies here and concluded no: unlike
  `L-020` (a content-extraction boundary, cheaply testable against static
  text with no external dependency), this invariant is a fact about an
  external tool's own CLI behavior, and the only call site
  (`buildDependencyTree`) already hardcodes `packageName` as a literal
  inline element of both argument lists — there is no code path through
  which this could silently regress without visibly rewriting that
  literal, and a test that actually caught a future regression here would
  need either a live `stack` invocation against a real monorepo fixture
  (a dependency this project's own established Haskell-adapter test
  posture deliberately avoids) or a refactor extracting args-construction
  into its own testable pure function (matching the precedent
  `buildTreeFromOutputs` already sets, but a new piece of production code
  this triage has no mandate to write or request unprompted). **Outcome:
  retain, not promote, not discard.** Real, specific, evidenced, and
  already fully resolved in the artifact it concerns — the fix is live,
  and the invariant is already recorded exactly where a future maintainer
  extending or debugging `Adapter.Deps`'s own logic would look, matching
  the same "a complete, sufficient record already exists at the source;
  no generalised destination is needed or exists" reasoning `L-019` used,
  not the "a wrong artifact would ship silently absent a promotion"
  reasoning that justified `L-020`/`L-021`/`L-024`. Revisit if: (a) a
  second external adapter (or a second Haskell command) shows the same
  bare-vs-explicit-`TARGET` shape, recurring the pattern generally enough
  to justify a `reference-project-protocol.md`- or `decisions/0057`-level
  note about external-CLI-tool argument scoping; or (b) `runStack`'s call
  sites are ever refactored to build args separately from the subprocess
  call, at which point a mocked-subprocess regression test asserting
  `packageName` is present in the constructed `TARGET` position becomes
  cheap and worth adding.
- **promoted_to:** — (retained; already documented in
  `adapters/haskell/src/Adapter/Deps.hs`'s own module-level haddock
  comment, lines 4-12, and the fix is already live at lines 43/47 — see
  curation note; no further artifact exists to promote into)

### L-024 — a context-packet's (and its upstream research's) "existing tests" trace must explicitly check for a schema/migration mechanism's own dedicated test file, not just the feature's own code-path tests

- **origin:** Phase 54c (evidence-backed, knowledge-based,
  documentation-first workflow), `doc-origin-pinned-reference` feature,
  discovered live during implementation, logged by whoever implemented
  per §6.1's own convention, not by `knowledge-curator` at assembly time
- **date:** 2026-09-18
- **project_revision:** working tree at `ae165e5` (Phase 54c
  implementation, uncommitted at filing time)
- **observation:** `context-packet.md`'s "Existing tests" section named
  only `tests/test_spec_docs.py` and `tests/test_doc_mapping.py` — both
  genuinely correct for `REQ-DOCORIGIN-002`/`-003` (the `scan_spec_docs`
  detection logic) — but never named `tests/test_graph.py`, which
  contains 6 pre-existing tests hard-coding the expected
  `_SCHEMA_VERSION` string. Implementing `REQ-DOCORIGIN-001` (the
  `_SCHEMA_VERSION` 6→7 bump) broke all 6, discovered only by running the
  full suite, not from anything in the packet. Root cause, per
  `packet-sufficiency.md`'s own classification: the Context Researcher's
  consumer-trace covered every real *code* consumer of `origin`
  exhaustively but never inspected the *test* file asserting the schema
  version literal — because no Observation/Evidence/Claim record had
  ever looked at `tests/test_graph.py`. A second, related gap in the same
  file: the established Phase 17/21/27/32 "fresh-DB acceptance test +
  migration test" pair pattern lives in `tests/test_graph.py` and was
  described narratively in the packet's "Relevant architecture" section
  but never pointed at its own file, so writing the two new mirroring
  tests required reading `tests/test_graph.py` directly to find the
  pattern rather than the packet naming it.
- **evidence:**
  `planning/knowledge/doc-origin-pinned-reference/packet-sufficiency.md`
  Gap 1 (`tests/test_graph.py`'s `test_init_schema_seeds_schema_version`,
  `test_init_schema_is_idempotent`, and four
  `test_open_graph_migrates_pre_phase_*` tests all hard-coding `"6"`) and
  Gap 2 (the Phase 17/21/27 pattern's own test-file location never named);
  `.claude/agents/context-researcher.md` step 6 ("Trace relevant tests,
  documentation, dependencies...") as it read before this triage — no
  language distinguishing a feature's own tests from a
  schema/migration-mechanism's dedicated test file.
- **classification:** scoped-rule (specific to `context-researcher`'s
  research procedure — and, secondarily, to what the packet-assembly mode
  can compact — when a Requirement touches a schema/migration/
  versioned-constant mechanism specifically; not a project-wide rule,
  since most features never touch such a mechanism)
- **status:** promoted
- **recurrence:** first occurrence
- **curation (Phase 54c triage, 2026-09-18, knowledge-curator):**
  provenance accepted — all required fields present (backfilled from the
  task's own description of `packet-sufficiency.md`'s findings).
  Independently re-read `packet-sufficiency.md` directly rather than
  taking the summary on faith: both gaps are recorded exactly as
  described, including the explicit classification "a one-off omission...
  not a structural knowledge-base gap" for Gap 1, and the note tying both
  gaps to the same generalisable lesson at the end of Gap 2. Independently
  re-read `.claude/agents/context-researcher.md` step 6 and confirmed it
  said nothing about schema/migration-specific test tracing before this
  triage's edit. Checked for a merge/duplicate candidate: grepped this
  inbox for "test_graph"/"migration test"/"schema" — no prior candidate
  addresses packet/research test-tracing completeness; not a duplicate of
  `L-021` (a *different* mechanism — a unit test bypassing a function's
  real production call site — this is a *trace-completeness* gap during
  research, not a wiring gap uncaught by an isolated unit test) or `L-016`
  /`L-020` (both about a different research artifact's own boundary/
  ambiguity, not about which test files get traced). Checked whether this
  belongs in `context-gaps/`: no — this is "how the research role should
  work" (what it traces), not a relationship CodeCompass's own graph is
  missing; correctly stays in `planning/learnings/`. **Outcome:
  promote.** Real, specific, evidenced by a genuine (if contained)
  implementation-time cost, the root cause is precisely diagnosed in
  `packet-sufficiency.md` itself (not speculative), and the fix is a
  small, concrete, low-risk addition to an existing research step —
  worth closing now, per the same reasoning `L-018`/`L-022` used for a
  first, well-evidenced near-miss. Destination:
  `.claude/agents/context-researcher.md` step 6 (the research role's own
  test-tracing step) — not `agent-led-workflow.md` or `CLAUDE.md`, since
  this is scoped to one experimental role's own research procedure, not a
  project-wide planning discipline; not the packet-assembly mode
  (`knowledge-curator`'s own brief) either, since packet assembly is
  "mechanical compaction" of what the knowledge base already contains —
  if no Claim/Evidence record ever inspected `tests/test_graph.py`, no
  amount of packet-assembly care could have surfaced it; the fix belongs
  upstream, at the point research traces are gathered. Per this task's own
  explicit grant, `.claude/agents/*.md` is not one of this agent's
  restricted files for this task — applying the edit directly rather than
  drafting-only.

  **Fix applied — `.claude/agents/context-researcher.md` step 6**, adding
  explicit schema/migration test-file guidance (see the file itself for
  the landed text; summary: when a Requirement touches a schema,
  migration, or versioned-constant mechanism, explicitly search for and
  inspect that mechanism's own dedicated test file — e.g. grep for the
  literal being changed or the migration function's name — not just the
  tests for the feature's own new code path, since a migration test
  asserting the old literal is a real consumer of that mechanism exactly
  as much as a code caller is).
- **promoted_to:** `.claude/agents/context-researcher.md` step 6
  (schema/migration-mechanism test-file check) @ (this phase's own
  closeout commit)

### L-023 — a newly-created `.claude/agents/*.md` file is not immediately dispatchable by its own type name (refined at Phase 79: a startup-latency condition, not a whole-session one)

- **origin:** Phase 54c (evidence-backed, knowledge-based,
  documentation-first workflow), retro "What didn't work" + "Lessons
  learnt"; filed at this triage's own initiative per the retro's own
  "Candidate learnings filed" note deferring the decision to
  `knowledge-curator`
- **date:** 2026-09-18
- **project_revision:** working tree at `ae165e5` (Phase 54c
  implementation, uncommitted at filing time)
- **observation:** two new `.claude/agents/*.md` files
  (`context-researcher.md`, `documentation-agent.md`) were created and
  committed to the working tree, then immediately dispatched via the
  `Agent` tool using the new type names. The first dispatch
  (`context-researcher`) failed outright with "Agent type
  'context-researcher' not found" despite the file already existing on
  disk — worked around by dispatching `general-purpose` with the role's
  full brief embedded in the prompt instead. Later in the same session,
  with no further action taken to cause it, a `documentation-agent`
  dispatch using the real type succeeded, and both real types worked
  correctly for every subsequent dispatch. The lead has no visibility
  into what triggered the registry to refresh, and no way to force a
  refresh on demand. This is an observation about the Agent-dispatch
  mechanism itself (Claude Code tooling), not about CodeCompass's own
  code, and is distinct in kind from every other `workflow`-classified
  candidate in this queue (`L-006`/`L-013`/`L-018`), which are all about
  *this project's own* dispatch-ordering/write-race discipline, not about
  the dispatcher's own registry timing.
- **evidence:** `planning/retros/phase-54c-evidence-knowledge-workflow.md`
  "Agents used" line and "What didn't work" (first bullet), both
  independently re-read rather than taken on the candidate's own
  characterization alone — the retro's account matches this entry's
  `observation` field exactly, including the explicit "for reasons this
  session doesn't have visibility into (not something to guess at
  further)" disclaimer.
- **classification:** workflow (a repeatable dispatch-procedure gap, in
  the same category `agent-led-workflow.md` already documents fixes for
  — `L-006`/`L-013`/`L-018` — even though the underlying cause here is
  outside this project's own control)
- **status:** promoted
- **recurrence:** first occurrence at Phase 54c; **recurred at Phase 79**
  (2026-10-01) — the same pattern (`implementation-reconstructor`, a
  newly-created type for that phase, failed its first dispatch with
  `Agent type 'implementation-reconstructor' not found`, was substituted
  with `general-purpose` for that first pass, then dispatched
  successfully under its real name later the same session, per a system
  notification) with a new detail the first occurrence didn't establish:
  once the real type name succeeded once, it kept working for every
  subsequent dispatch that session — the limitation is a one-time
  startup-latency condition per session, not one that recurs on every
  dispatch attempt within a session. See the Phase 79 curation note below.
- **curation (Phase 54c triage, 2026-09-18, knowledge-curator):**
  provenance accepted — all required fields present. Independently
  re-read the retro's own "What didn't work" and "Lessons learnt"
  sections directly rather than trusting only this task's summary of
  them — both match, including the retro's own generalised framing ("A
  phase that dogfoods its own newly-created infrastructure... should
  have a disclosed fallback ready rather than treating the first dispatch
  failure as a blocker"). Checked for a merge/duplicate candidate:
  grepped this inbox for "registry"/"Agent type"/"not found" — no prior
  candidate addresses agent-dispatch registry timing; not a duplicate of
  `L-018` (a `Write`-race between two concurrently-dispatched agents — a
  different mechanism entirely, file-clobbering vs. type-not-found) or
  `L-006`/`L-013` (roadmap/`CONTEXT.md` reconciliation timing, not
  dispatch availability). Checked whether this belongs in `context-gaps/`
  or `context-observations/` instead: no to both — this is not a
  relationship CodeCompass's own graph is missing, nor an experience with
  an existing graph edge; it is a process-doc gap in how this project's
  own agent-led workflow handles introducing a *new* agent type
  mid-session, so it correctly stays in `planning/learnings/`. **Outcome:
  promote (recommendation + draft; does not land here — the recommended
  destination, `planning/agent-led-workflow.md`, is outside this agent's
  write boundary — `planning/learnings/**` / `planning/context-gaps/**` /
  `planning/context-observations/**` / `planning/knowledge/**` /
  draft files under `planning/` only — and this task's explicit grant of
  direct edit access was scoped to `.claude/agents/*.md` specifically,
  for `L-024`, not to `planning/agent-led-workflow.md`).** Real,
  specific, single-occurrence but fully evidenced with a concrete,
  already-working fallback in hand (unlike a purely hypothetical
  concern) — worth recording as a known, disclosed operational gap now,
  per the same "close it while the fallback is fresh and evidenced"
  reasoning `L-018` used, rather than waiting for a second phase to
  independently rediscover the same failure and the same workaround.
  Explicitly **not** recommending a fix to the dispatcher/tooling itself
  (out of this project's control and out of scope for `planning/**`) —
  only a process-doc note so a future session doesn't treat the first
  dispatch failure as a blocker.

  **Recommended fix — add a note near step 5 of
  `planning/agent-led-workflow.md`** (draft, for the lead to review and
  land; not applied here):

  > **If this phase created a new `.claude/agents/*.md` file in this same
  > session, its real type name may not be immediately dispatchable.**
  > The dispatcher's own agent registry appears to load at some point
  > other than "the moment the file exists," and there is no known way to
  > force a refresh. Observed at Phase 54c: the first dispatch of a
  > newly-created type failed with `Agent type '<name>' not found`
  > despite the file already being committed to the working tree; the
  > same type dispatched correctly later in the same session, for reasons
  > not visible from within the session. Do not treat the first failure
  > as a blocker — fall back to dispatching `general-purpose` with the
  > new role's full brief embedded in the prompt for that first pass, and
  > retry the real type name on a later dispatch; it has, so far, always
  > become available later in the same session. (Phase 54c — L-023.)

  Deliberately scoped to "a brand-new agent type created this session,"
  not a general dispatch-reliability caveat — every already-established
  roster entry (`.claude/agents/` files that predate the current session)
  has never shown this failure. Revisit/withdraw if a future phase
  creates a new agent type and it dispatches correctly on the first try
  (suggesting this was a one-time artifact of this specific session
  rather than a standing property of new-file registration), or if the
  user judges a single, self-resolving incident with a working fallback
  already in hand doesn't warrant a standing process-doc note.
- **curation (Phase 79 triage, 2026-10-01, knowledge-curator) — recurrence
  + wording refinement, not a new candidate:** origin: Phase 79
  (clean-room conceptual understanding + documentation reconstruction,
  `decisions/0066`) retro "What didn't work" (second bullet). Checked
  first, per this triage's own instruction, whether `L-023` already
  exists before filing anything new — it does (above) — so this is
  logged as a recurrence + refinement of that entry, not a new `L-NNN`.
  Independently re-read `planning/retros/phase-79-clean-room-understanding-and-documentation-reconstruction.md`
  "What didn't work" (second bullet) directly: confirms the
  `implementation-reconstructor` type (newly created this phase, per
  `decisions/0066`) was used via the `general-purpose` substitute for its
  first dispatch, then dispatched successfully by its own type name later
  the same session, "confirmed by a system notification" — the same
  failure→fallback→later-success shape `L-023` already documents, not a
  new mechanism.

  The retro's own proposal is a *wording* refinement, not a new rule:
  the landed text in `planning/agent-led-workflow.md` step 5 (the
  paragraph beginning "If this phase created a new
  `.claude/agents/*.md` file in this same session...") already tells a
  future session to retry the real type name later and not treat the
  first failure as a blocker, but it stops short of saying what to do
  *after* that retry succeeds — a future session reading only "it has,
  so far, always become available later in the same session" could
  reasonably (over-)read this as "keep using the `general-purpose`
  substitute for the rest of the session to be safe," which is not what
  either occurrence actually showed: at both Phase 54c and Phase 79, once
  the real type name worked once, it worked for every subsequent
  dispatch, with no further degradation. That is a startup-latency
  condition (the registry refreshes once, at some point outside the
  session's visibility, and then stays refreshed), not a whole-session
  limitation — worth saying explicitly so a future phase doesn't over-apply
  the workaround.

  **Outcome: merge/refine `L-023` in place — recommend appending one
  clarifying sentence to the already-landed
  `planning/agent-led-workflow.md` step 5 paragraph** (draft, for the
  lead to review and land; not applied here, since `agent-led-workflow.md`
  is outside this agent's write boundary):

  > **This is a startup-latency condition, not a whole-session
  > limitation.** Once the real type name succeeds on a retry, treat it as
  > available for every remaining dispatch that session — don't keep
  > using the `general-purpose` substitute on the assumption that one
  > early failure means it's needed for the rest of the session. Confirmed
  > at Phase 79: the same failure → substitute → later-success pattern
  > recurred for a different newly-created type
  > (`implementation-reconstructor`), and once it worked once, it worked
  > for every subsequent dispatch that phase, with no further failures.
  > (Phase 79 — L-023.)

  Does not withdraw or weaken the original note — the first-dispatch
  failure and its fallback are still real and still recurred exactly as
  described; this only adds the missing "and then what" half. Recommend
  a corresponding `promoted.md` addendum once landed: `L-023 |
  2026-10-01 | workflow | planning/agent-led-workflow.md step 5 (refined:
  explicit startup-latency framing, confirmed by a second, independent
  recurrence at Phase 79) @ (Phase 79's own closeout commit)`.
- **promoted_to:** — (pending; recommendation drafted above, awaiting
  lead review — `agent-led-workflow.md` is outside this agent's write
  boundary)

### L-022 — a hand-authored "authoring rationale" field in evaluation material is not internal commentary if the renderer writes it into the agent-visible output

- **origin:** Phase 54b (Ledgerkit behavioural-understanding experiment),
  the lead's own material-construction pass while extending Phase 54's
  reference-ingestion pipeline for the treatment run's indexed corpus;
  self-caught before either agent was dispatched; filed at the lead's own
  request that `knowledge-curator` judge whether it warrants an `L-NNN`
- **date:** 2026-09-18
- **project_revision:** working tree at `d85ac34` (Phase 54b
  implementation, uncommitted at filing time)
- **observation:** the first draft of `references.toml`'s `label`/`note`
  fields for this task's newly-added depth-related selections stated the
  lead's own analysis of the correct answer directly — e.g. a label
  literally reading "depth-trap-matchesaccount" and a note beginning "THE
  TRAP: ... is the exact evidence Ledgerkit's own Stage C Phase 1 read
  before wrongly classifying depth: ...", another beginning "THE
  EXCEPTION: ... a real, deliberate, source-confirmed divergence...".
  `reference_pipeline.py::render_extracted_markdown` renders **both**
  `selection.label` (as the extracted file's own H1) and `selection.note`
  (as visible prose immediately beneath it) into the `.md` file
  `sync`/`query relations` exposes and a dispatched agent reads directly
  — there is no separate channel for "authoring-only" commentary; a
  `references.toml` field reads like private authoring rationale but is,
  in fact, agent-visible output verbatim. The lead caught this only by
  rereading `render_extracted_markdown`'s own source (not the authoring
  schema/interface) before either run was dispatched, confirmed `note` is
  genuinely written into the rendered body rather than staying in
  `references.toml`'s own TOML comments, and rewrote every label/note for
  this task's selections to strictly neutral file/function-location text
  before either agent ran. Had this rendering path not been re-checked,
  the treatment agent would have been handed the experiment's own correct
  answer inside its own "indexed material," and the resulting report
  would have read as an ordinary, well-reasoned finding — the flaw would
  have been undetectable from the report itself, silently invalidating
  the entire baseline-vs-treatment comparison this class of experiment
  exists to run (a controlled comparison's whole value rests on neither
  arm being handed the answer).
- **evidence:**
  `planning/reference-projects/ledgerkit/reference-experiment/reference_pipeline.py::render_extracted_markdown`
  (lines 316-352 — both `f"# {selection.label}"` and `selection.note` are
  written into the returned Markdown body, confirmed by direct read, not
  by trusting the lead's own account); the current, fixed
  `references.toml` entries for every depth-related selection (e.g.
  `label = "query-hs-matchesaccount"` / `note = "matchesAccount,
  Hledger/Query.hs, in full."`, and identically plain, file/function-only
  text for `depth-manual-section`, `depth-query-manual-section`,
  `multibalancereport-hs-a`/`-b`, `postingsreport-hs-a`/`-b`,
  `entriesreport-hs`, `accounts-hs`, `accounttransactionsreport-hs`,
  `ledger-hs`) — none of the 9 depth-related selections' current
  label/note text contains any analysis, verdict, or forward-looking
  claim; `planning/reference-projects/ledgerkit/findings.md`'s Phase 54b
  section, "Setup" paragraph, independently corroborating the near-miss
  ("an early draft's labels/notes stated the answer outright, e.g. 'THE
  TRAP', 'THE EXCEPTION'; caught and rewritten to plain file/function
  identification before either agent ran, since the experiment would have
  been worthless otherwise").
- **classification:** scoped-rule (specific to constructing hand-authored
  material a dispatched agent-under-test will read as part of a
  controlled reference-project experiment — narrower than a project-wide
  `CLAUDE.md` rule, since it doesn't bind ordinary phase work outside this
  experimental-design pattern, and Phase 54's own earlier ingestion work
  never carried this risk in practice, since it had no "trap"/decoy
  structure for a note to leak)
- **status:** promoted
- **recurrence:** first occurrence
- **curation (Phase 54b triage, 2026-09-18, knowledge-curator):**
  provenance accepted — all required fields present. Independently
  re-derived the central claim rather than taking the lead's own account
  on faith: read `reference_pipeline.py::render_extracted_markdown`
  directly and confirmed both `selection.label` (as the file's `# `
  heading) and `selection.note` (as a body paragraph immediately after
  it) are written into the string `write_extracted_markdown` then persists
  to disk — genuinely agent-visible output, not retained only in
  `references.toml`'s own authoring-time structure. Read the current
  `references.toml` directly and confirmed every one of the 9 depth-
  related selections' `label`/`note` pairs is now strictly neutral
  (file/function identification only, e.g. "An excerpt of
  Hledger/Reports/MultiBalanceReport.hs.") — the fix described did
  genuinely land, not just get claimed. Cross-checked against
  `findings.md`'s own Phase 54b section, which independently corroborates
  the same incident from the experiment-record side, not merely
  restating the lead's own words. This is a real, evidenced,
  non-hypothetical near-miss, distinct from `L-014` (a stale
  *background/rationale* claim in a plan file, discarded because it
  caused no wrong action and no artifact needed correcting): here, a
  wrong artifact **would** have been dispatched to an agent and consumed
  as ground-truth-shaping context, with the resulting report giving no
  internal signal of the contamination — closer in shape to `L-021`
  (a defect that would have shipped as "done" had an independent
  re-derivation not caught it) than to L-014's harmless stale-claim
  case, even though here the lead's own re-check caught it before
  dispatch rather than an independent agent catching it after
  implementation. Checked for a merge/duplicate candidate: grepped this
  inbox and `promoted.md` for "contaminat"/"leak"/"rendering" — no prior
  candidate addresses hand-authored evaluation-material construction;
  `phase-54b-ledgerkit-behavioural-understanding-experiment.md` §4.1's
  own "avoiding lead-contamination" design point is about *who* is
  dispatched (a fresh agent, not the lead), a different, already-
  addressed risk from *what content* a fresh agent is handed — not a
  duplicate. Checked whether this belongs in `context-gaps/` instead: no
  — this is "how we should work" when authoring evaluation material, not
  a relationship CodeCompass's graph is missing; correctly stays in
  `planning/learnings/`. **Outcome: promote (recommendation + draft;
  does not land here).** Real, specific, evidenced by a genuine
  near-miss with a severe (if narrowly averted) consequence, and the fix
  is a small, concrete, low-risk addition to an existing per-task
  procedure — worth closing now rather than waiting for a second,
  actually-realized instance. Destination: `planning/v1-redefinition/
  reference-project-protocol.md` §2.4 (the per-task procedure every
  controlled reference-project experiment already instantiates), not a
  `.claude/` skill/agent-brief — matching the `L-013`/`L-018` precedent
  of landing a workflow-scoped fix in the actual governing process
  document rather than forcing it into the classification table's literal
  Skill-file mapping. Not `CLAUDE.md`/`proposed-governance-changes.md`:
  this rule is scoped to constructing evaluation material for a
  controlled experiment specifically, not a project-wide agent
  discipline, so `CLAUDE.md` §0's heavier review bar does not apply —
  `reference-project-protocol.md` is outside this agent's write boundary
  regardless, so the lead applies the diff below.

  **Recommended fix — add a step to `reference-project-protocol.md` §2.4**
  (draft, for the lead to review and land; does not apply to genuine-task
  evaluations that use only the target repo's own real, unauthored
  content, since those carry no equivalent commentary field to leak):

  > **Before dispatching any run, when the per-task procedure includes
  > constructing hand-authored material a dispatched agent-under-test
  > will read** (e.g. a reference-ingestion excerpt's `label`/`note`
  > fields, a synthetic fixture file, any authoring-time rationale meant
  > to explain *why* a selection was made) — re-verify, by reading the
  > actual rendering/output function itself (not just the authoring
  > schema or interface), that no field intended only as internal
  > authoring commentary is actually written into the agent-visible
  > output. A field named `note` or similar reads as private authoring
  > rationale; if the renderer writes it into the file body, it is
  > agent-visible content indistinguishable from the rest of the
  > material. Confirmed the hard way at Phase 54b (`L-022`): an early
  > draft's `note` fields stated the experiment's own correct answer
  > outright and would have silently invalidated the entire
  > baseline-vs-treatment comparison had the rendering path not been
  > re-checked before either agent was dispatched.

  This is deliberately scoped to controlled experiments that construct
  hand-authored material for a dispatched agent to read, not a general
  "review your work" restatement — genuine-task evaluations (§2.3/§2.4's
  ordinary case) use the target repo's own real content and carry no
  equivalent risk. Revisit/withdraw if a second controlled-experiment
  phase never recurs this shape, or if the user judges the existing
  "genuine work only"/independence discipline already sufficient once
  this specific incident is pointed out.
- **promoted_to:** — (pending; recommendation drafted above, awaiting
  lead review — `reference-project-protocol.md` is outside this agent's
  write boundary)

### L-021 — a unit test that calls a function directly, bypassing its real production call site, cannot catch a wiring gap at that call site

- **origin:** Phase 55b (spec-doc name population, closing `CG-004`), retro
  "Lessons learnt" #1 + "Process-improvement feedback"; filed at the
  retro's own explicit request that `knowledge-curator` judge whether this
  warrants its own `L-NNN` during this phase's triage
- **date:** 2026-09-17
- **project_revision:** working tree (Phase 55b's own uncommitted diff at
  filing time)
- **observation:** Phase 55b's first implementation attempt populated
  `doc_artifacts.name` for `spec_doc` rows (`spec_docs.py::_extract_title`)
  and added every new unit test the plan called for
  (`test_spec_docs.py`/`test_doc_mapping.py`) — all green on the first
  run. It was still completely non-functional in the real, running tool:
  `sync.py::rebuild_project_graph`'s own call to
  `build_doc_relations_edges` never included `spec_doc_rows` in the third
  (target) argument, so the real gap `CG-004` existed to close still
  reproduced identically against the live Ledgerkit repository. No unit
  test caught this, because every one of them called
  `build_doc_relations_edges` (or `scan_spec_docs`) directly — none went
  through `sync.py`'s real production wiring, the one place the actual
  defect lived. This was caught only by `context-evaluator`'s round-1
  independent pass, which re-ran the real tool against real data rather
  than trusting the unit tests' own pass/fail — not by the lead's own
  confidence in the green suite, which had no internal signal telling it
  to distrust that confidence. The phase's own plan
  (`phase-55-evidence-reconciliation.md` §G) listed `sync.py` under
  "Affected architecture" but never required a test through it — the
  test-plan gap was in the plan document itself, not only in what the
  implementing pass chose to write.
- **evidence:** `planning/retros/phase-55b-spec-doc-name-population.md`
  "Scope delivered vs planned" ("A more consequential failure..."),
  "Lessons learnt" #1, "Process-improvement feedback" (all three
  independently re-read, not taken on the retro's own characterization
  alone); `src/codecompass/sync.py`'s current
  `build_doc_relations_edges(spec_doc_rows + vendor_upstream_doc_rows,
  configs, vendor_doc_rows + vendor_upstream_doc_rows + skill_doc_rows +
  spec_doc_rows, project_root)` call, confirming `spec_doc_rows` is now
  present in the target argument (the round-2 fix); `tests/test_sync.py::test_rebuild_project_graph_relates_two_spec_docs_to_each_other`,
  whose own docstring names exactly this failure mode ("caught missing by
  an independent `context-evaluator` pass before this test existed: the
  unit-level tests passed even when `spec_doc_rows` was never added to
  `build_doc_relations_edges`'s target argument in `sync.py`") — the only
  test in this phase's diff that calls `rebuild_project_graph` itself
  rather than `build_doc_relations_edges`/`scan_spec_docs` directly.
- **classification:** project-rule (a recurring project-wide planning
  discipline, not scoped to the agent-led workflow's own step ordering or
  to one agent role — it binds whoever writes a phase plan, agent-led or
  not, per `CLAUDE.md` §1's existing "how the phase will be verified as
  done" clause, which this candidate proposes strengthening rather than
  replacing)
- **status:** promoted — `CLAUDE.md` §1 amended (mirrored in
  `CONTRIBUTING.md`), user-approved via `AskUserQuestion` ("Approve as
  written"), landed in the follow-up commit after Phase 55b's own
  closeout; see `planning/learnings/promoted.md`.
- **recurrence:** first occurrence (as a filed candidate; the retro itself
  frames the underlying principle as general/durable, not a one-off)
- **curation (Phase 55b triage, 2026-09-17, knowledge-curator):** provenance
  accepted — all required fields present. Independently re-derived the
  claim from the real diff rather than trusting the retro's own account:
  confirmed `sync.py`'s `build_doc_relations_edges` call genuinely now
  includes `spec_doc_rows` in its target argument (the round-2 fix), and
  confirmed `test_rebuild_project_graph_relates_two_spec_docs_to_each_other`
  is the one test in this phase's diff that exercises the real production
  entry point rather than the function in isolation — every other new
  test in `test_spec_docs.py`/`test_doc_mapping.py` does call the target
  function/module directly, exactly as the candidate describes. This is a
  real, evidenced, non-hypothetical incident: a phase whose own plan
  named `sync.py` as affected architecture still shipped a
  production-broken first attempt, caught only by independent evaluation
  re-deriving the real-world claim from scratch. **Two components,
  weighed separately, per this project's own discipline of not bundling
  distinct findings into one promotion:**
  1. *The general methodological claim* ("a unit test bypassing a
     function's real call site can't catch a wiring gap there") is not
     novel software-engineering knowledge in the abstract — it is a
     well-known integration-vs-unit-test distinction — but this project
     has never once named it as its *own* standing discipline before, and
     this is the first time it concretely cost a phase a wasted
     implementation round, independently caught rather than silently
     absorbed. Distinct from `L-014` (a plan's *background/rationale*
     claim going stale, discarded because no wrong action resulted) —
     here a wrong artifact *was* shipped and would have been committed as
     "done" had round 1's green tests been trusted.
  2. *The procedural fix* ("any phase adding behavior to an existing
     multi-argument function with a real production call site must name
     that call site explicitly in the plan's own test/verification
     section, and include at least one test through it") is concrete,
     low-risk, and directly actionable as a `CLAUDE.md` §1 strengthening —
     §1 already requires a plan to describe "how the phase will be
     verified as done"; this closes a specific, evidenced way that clause
     can be satisfied on paper (unit tests exist, plan says "tested") while
     still failing in exactly the way this phase failed.
     Checked whether `planning/agent-led-workflow.md` is the better home
     instead (matching `L-006`/`L-013`/`L-018`'s precedent): those three
     are about the *agent-orchestration* procedure specifically
     (dispatch ordering, roadmap-flip timing, concurrent-write races) —
     narrower in scope than this candidate, which is about what a phase
     *plan's own content* must specify regardless of which agent or the
     lead writes it, and would bind even a hypothetical non-agent-led
     contributor following `CONTRIBUTING.md`. `CLAUDE.md` §1 already
     governs plan content project-wide; this is a targeted strengthening
     of an existing clause there, not a new agent-workflow step. Checked
     for a merge/duplicate candidate: grepped this inbox and
     `promoted.md` for "call site"/"wiring gap"/"production entry
     point" — no prior candidate names this specific failure mode; not a
     restatement of `L-011` (a different mechanism — `check_generated_
     artifacts_match_source`'s no-graph-yet false-positive, a detection
     bug in an existing check, not a missing test-through-call-site
     requirement) or `L-005` (`docs-maintainer` editing a generated file
     instead of its generator — a different kind of "wrong layer"
     mistake). **Outcome: promote (recommendation + draft; does not land
     here — `CLAUDE.md` is outside this agent's write boundary per its
     own hard rules, and per `CLAUDE.md` §0 itself any change to that
     file requires the user's explicit review as a diff before being
     written; propose only via
     `planning/v1-redefinition/proposed-governance-changes.md`, which
     this triage does below).**

  **Recommended fix — strengthen `CLAUDE.md` §1's existing verification
  clause** (draft, added to
  `planning/v1-redefinition/proposed-governance-changes.md` §D for the
  lead to review and present to the user; not applied here):

  > Append to §1, after the existing "If writing the plan surfaces an
  > assumption not already settled, pause and ask before proceeding from
  > plan to code" sentence:
  >
  > If a phase adds behavior to an existing function that already has a
  > real production call site, the plan's verification section must name
  > that call site explicitly and include at least one test that
  > exercises it directly — a test that only calls the changed function
  > in isolation is not sufficient on its own, no matter how thorough,
  > since it cannot catch the function's new behavior never actually
  > being wired into its caller. (Phase 55b — L-021.)

  This is deliberately scoped to the exact failure shape this candidate
  evidences (a real call site already exists; the plan already names the
  affected file; only the test-through-that-call-site requirement is
  missing) rather than a broader "always write integration tests" rule
  this one incident doesn't yet justify. Revisit/withdraw if the user
  judges §1's existing "how the phase will be verified as done" language
  already sufficient once this specific incident is pointed out — that is
  the user's call at gate G4, not this triage's.
- **promoted_to:** — (pending; recommendation drafted in
  `proposed-governance-changes.md` §D, awaiting lead review + user
  approval per `CLAUDE.md` §0's own requirement for any change to that
  file)

### L-020 — content-hash pinning proves an excerpt hasn't silently changed; it does not prove the excerpt's boundary covers what its own description claims

- **origin:** Phase 54 (heterogeneous reference-material experiment), the `tag:` query semantics treatment run, independently caught by `context-evaluator`'s evaluation
- **date:** 2026-09-16
- **project_revision:** working tree at `72961e0`; `planning/reference-projects/ledgerkit/reference-experiment/` untracked (outside `src/codecompass/` per this phase's own design decision)
- **observation:** `references.toml`'s `tag-query-manual` selection was hand-authored with `lines = [7372, 7392]` and a `note`/frontmatter description claiming the excerpt contained "the three inheritance rules (accounts from parents, postings from account+transaction, transactions from postings)." The real hledger manual's third rule ("Transactions also acquire the tags of their postings") is at lines 7393-7394 — one bullet past the selection's own end line, and therefore genuinely absent from the extracted, hashed artifact, even though the artifact's own description confidently claimed otherwise. `references.lock`'s content hash for this selection is completely correct (it hashes exactly what was extracted, byte for byte) — the hash guarantees the excerpt hasn't silently drifted since extraction; it says nothing about whether the excerpt's boundary was drawn correctly in the first place. The treatment brief then repeated the false claim as fact ("all three inheritance rules present and precise... verbatim"), which `context-evaluator`'s independent line-by-line check against the real pinned source caught and correctly rated **FAIL** (the phase's own evaluation report, not this entry, is the authoritative verdict). This is exactly the "confidently wrong, presented authoritatively" failure mode this project's own evaluation rubric treats as worse than an honest gap — and it happened inside the very artifact whose entire value proposition (a provenance hash) is "trust this without re-checking it yourself."
- **evidence:** `planning/reference-projects/ledgerkit/reference-experiment/54-tag-query-semantics-reference-experiment-evaluation.md` (the independent FAIL verdict, §"Independent findings" item 2); `hledger/hledger.1:7388-7394` in the pinned local hledger clone (`/home/cormac/projects/hledger`, commit `33fa849e7ae841968bd21c427094c4fb4a4ec38d`) directly confirms the third rule sits at lines 7393-7394; `references.toml`'s git history in this same phase shows the selection corrected to `lines = [7372, 7394]` afterward, with a new regression test (`tests/test_reference_pipeline.py::test_tag_query_manual_excerpt_contains_all_three_inheritance_rules`) added to catch a recurrence.
- **classification:** invariant (a general property of any content-hash-pinned extraction pipeline, not scoped to this one experiment or this one hledger section)
- **status:** promoted — `tests/test_reference_pipeline.py::test_tag_query_manual_excerpt_contains_all_three_inheritance_rules` landed in commit `a4e58da` (this phase's own closeout commit); see `planning/learnings/promoted.md`.
- **recurrence:** first occurrence
- **curation (Phase 54 triage, 2026-09-16, knowledge-curator):** provenance
  accepted — all required fields present. Independently re-verified against
  the real pinned hledger source rather than taking the entry's own
  citation on faith: read `/home/cormac/projects/hledger/hledger/hledger.1`
  lines 7368-7394 directly — confirms the three inheritance bullets sit at
  line 7390 ("Accounts also inherit the tags of their parent accounts"),
  line 7392 ("Postings also inherit the tags of their account and their
  transaction"), and lines 7393-7394 ("Transactions also acquire the tags
  of their postings"), and that the original `[7372, 7392]` selection range
  therefore byte-accurately extracts *up to* line 7392 while excluding the
  third rule entirely — exactly as claimed, confirmed by direct read, not
  by trusting the evaluation report's word for it. Cross-checked against
  `54-tag-query-semantics-reference-experiment-evaluation.md`'s independent
  FAIL verdict (finding 2) and confirmed the phase's own fix has already
  landed in the working tree: `references.toml`'s `tag-query-manual`
  selection now reads `lines = [7372, 7394]` with an explanatory correction
  comment, `references.lock`'s content hash for that selection has been
  regenerated (`sha256:4672d39a...`, differing from the pre-fix
  `sha256:1590e35d...` still quoted, deliberately unedited, in
  `treatment-tag-query-brief.md`'s Step 2), and a new regression test —
  `planning/reference-projects/ledgerkit/reference-experiment/tests/test_reference_pipeline.py::test_tag_query_manual_excerpt_contains_all_three_inheritance_rules`
  — directly asserts all three inheritance-rule sentences appear in the
  extracted text, guarding a recurrence of exactly this defect (confirmed
  by reading the test itself, not just its name). Checked for a
  merge/duplicate candidate: grepped `promoted.md` and this inbox for any
  prior invariant about content-hash pinning or extraction-boundary
  correctness — none exists; not a restatement of `L-005`/`L-011` (both
  about `check_generated_artifacts_match_source`, a different check and a
  different failure mechanism — sync-state, not human-drawn extraction
  boundaries). **Outcome: promote.** Classification `invariant` maps to "a
  regression test" per `learning-lifecycle.md` §4, and that test already
  exists, landed within this same phase, directly encoding the invariant
  this candidate names (a content-hash's immutability guarantee is a
  different guarantee than its boundary's correctness) rather than merely
  re-testing the narrower `tag:`-specific outcome. This does not depend on
  Phase 55/GATE DD's separate, larger decision about whether to generalise
  the ingestion pipeline into `src/codecompass/` — the invariant is general
  by its own classification text, and the test's current location inside
  `planning/reference-projects/ledgerkit/reference-experiment/tests/`
  (deliberately outside `src/codecompass/` per this phase's own design
  decision) is the correct home for it today, the same way
  `tests/fixtures/ledgerkit_lifecycle_demo/`'s own regression coverage
  stays outside the shipped package until a later phase (if ever)
  generalises the mechanism itself. Worth naming explicitly for whoever
  later picks up that generalisation: the boundary-vs-immutability
  distinction should travel with the pipeline as its own regression test in
  `tests/`, not be assumed automatically subsumed by a content-hash check
  alone — not a new candidate learning, just a forward note attached to
  this one. **Not flipping `status` to `promoted` yet, deliberately**:
  `planning/reference-projects/ledgerkit/reference-experiment/` is still
  untracked per `git status` as of this triage — the regression test is
  real and present in the working tree but has not "actually landed" in
  the sense this agent's own hard rule requires before a `promoted.md`
  pointer is written. Recommend: once Phase 54's closeout commit lands
  (this triage's own edits included), flip `status` to `promoted` and add
  `L-020 | 2026-09-16 | invariant |
  planning/reference-projects/ledgerkit/reference-experiment/tests/test_reference_pipeline.py::test_tag_query_manual_excerpt_contains_all_three_inheritance_rules
  @ <real short SHA>` to `promoted.md` — mirroring exactly how `L-016`/
  `CG-002` deferred their own `promoted.md` line until Phase 49's fix was
  confirmed actually committed. **promoted_to:** left blank below until
  that commit exists.
- **promoted_to:** — (pending; see curation note — flip once Phase 54's
  closeout commit lands)

### L-019 — a fixture bootstrapped from a hand-written placeholder that `codecompass sync` also mechanically regenerates causes a one-time content-hash "false churn"

- **origin:** Phase 52 (context edge lifecycle demonstration, local fixture `tests/fixtures/ledgerkit_lifecycle_demo/`)
- **date:** 2026-09-14
- **project_revision:** working tree at Phase 52 (pre-commit)
- **observation:** the fixture's `.claude/skills/codecompass/SKILL.md` was hand-written with a short placeholder `description:` field before the first `codecompass --budget 0` run. That same first sync's own bootstrap pipeline mechanically regenerated the file (the real, longer tool-Skill description) as a side effect *within the same invocation* that also scanned it for `doc_artifacts.description` — so the very first `relation_enrichment.select_candidates()` call computed its content-hash against the placeholder's short text, while every subsequent read (including a second `enrich apply` resubmission in the same demo, cycle 2) saw the regenerated, longer text. `select_candidates` correctly judged the edge "changed" given that real difference — this is the caching mechanism working exactly as designed, not a defect — but it meant an intended "resubmit an unchanged edge, expect rejection" test step instead legitimately re-applied, and a follow-up genuinely-clean resubmission was needed to actually demonstrate the rejection path. Confirmed the underlying Skill generation is deterministic/idempotent once past this one-time transient (`md5sum` identical across two consecutive `codecompass index` runs with no other changes).
- **evidence:** `tests/fixtures/ledgerkit_lifecycle_demo/DEMO.md` step 9 (full root-cause trace); direct `sqlite3` reads of `doc_relation_enrichment.content_hash`/`generated_at` before and after; a manual hash recomputation confirming the current (source, target) pairing matches the "changed" hash, not the original cached one.
- **classification:** scoped-rule (a fixture/test-authoring methodology note, not a CodeCompass product defect)
- **status:** retained
- **recurrence:** first occurrence
- **curation (Phase 52 triage, 2026-09-14, knowledge-curator):** provenance
  accepted — all required fields present. Independently re-verified against
  `tests/fixtures/ledgerkit_lifecycle_demo/DEMO.md` step 9 (not just this
  entry's own prose): the transcript's account of the root cause (the
  fixture's hand-written placeholder `.claude/skills/codecompass/SKILL.md`
  description being mechanically regenerated by the same `codecompass
  --budget 0` invocation that also scanned it, so cycle 2's first
  resubmission of `dev-docs/retros/README.md`'s edge computed against a
  content-hash captured before that regeneration and was legitimately
  judged "changed") matches this candidate's `observation`/`evidence`
  fields exactly, down to the "`md5sum` identical across two consecutive
  `codecompass index` runs" determinism check confirming this was a
  one-time bootstrap-order transient, not a standing cache defect. Also
  cross-checked against `planning/context-observations/OBS-006`'s "wrong or
  misleading?" field, which independently corroborates the same root cause
  and explicitly defers to this entry rather than duplicating it — no
  contradiction between the two records. **Outcome: retain, not promote,
  not discard.** Checked whether this counts as "already landed" rather
  than needing a fresh promotion, per this phase's own framing: `DEMO.md`
  step 9 already documents the root cause, the reasoning that
  `select_candidates` behaved correctly, and the explicit labelling "a
  methodology note for future fixture/demo authors, not a product defect"
  — that is a complete, sufficient record for anyone re-running or
  extending *this specific fixture* in the future, and needs no duplicate
  write. What DEMO.md's own documentation does **not** yet do is
  generalise the note into a rule any *future, different* fixture author
  would consult before hitting the same trap — and no such destination
  exists to promote into: grepped `CONTRIBUTING.md` for "fixture" (no
  hits — no fixture-authoring section exists there today), and confirmed
  by listing `tests/fixtures/` that no other fixture in this repo runs a
  live `codecompass` invocation against a hand-authored mini-repo
  containing its own placeholder generated artifact (`SKILL.md`) the way
  this one does — every other fixture is a static input file for
  unit-level mocking, not a full sync-cycle demonstration environment.
  This is genuinely single-occurrence with no existing generalised home,
  not a recurring pattern being left unaddressed. Recommended destination
  if a second instance appears: a short "authoring a local fixture that
  runs a real `codecompass` sync cycle" note — either a new
  `tests/fixtures/README.md` or a `CONTRIBUTING.md` testing section, "seed
  any generated/mechanically-regenerated artifact (e.g. a tool `SKILL.md`)
  with its *real* expected post-sync content up front, not a placeholder,
  to avoid a one-time content-hash transient on the very first sync" — a
  lead/`docs-maintainer` decision once there's a second fixture of this
  shape to generalise from, not before. Revisit on: (a) a second
  local-fixture lifecycle/enrichment demo hitting the same placeholder+
  regeneration shape, or (b) this exact fixture being reused/extended in a
  later phase (e.g. a Phase 55+ context-observations consolidation) in a
  way that re-triggers the same transient.
- **promoted_to:** — (retained; `DEMO.md` step 9 already serves as the
  sufficient record for this specific fixture; no generalised destination
  exists yet to promote into — see curation note)

### L-018 — dispatching two agents to `Write` (not `Edit`) the same file path concurrently silently loses one agent's output

- **origin:** Phase 46 (`planning/retros/phase-46-ledgerkit-tasks.md`, "What didn't work" + "Process-improvement feedback")
- **date:** 2026-09-13
- **project_revision:** b0717ee (CodeCompass HEAD when the race occurred)
- **observation:** `reference-project-tester` and `context-evaluator` were dispatched concurrently, both instructed to write independent sections to `planning/reference-projects/ledgerkit/01-query-semantics.md`, each told to check the file's current state before writing. `context-evaluator` reported successfully writing its report and returned a detailed, accurate summary of its findings. When the lead read the file afterward, only `reference-project-tester`'s section was present — a placeholder comment marking where `context-evaluator`'s section should go was still unfilled. Root cause: `Write` replaces the entire file rather than appending; `reference-project-tester`'s later `Write` call silently clobbered `context-evaluator`'s earlier one, and "check the file first" instructions cannot prevent this race between two independently-scheduled background agents. The lead caught this only by reading the actual file after both agents completed and cross-referencing it against `context-evaluator`'s own returned summary — without that verification step, a real independent verdict (CodeCompass's second FAIL) would have been silently absent from the permanent record while the task-completion report claimed success.
- **evidence:** `planning/reference-projects/ledgerkit/01-query-semantics.md`'s git history in this phase's uncommitted diff (a single `## reference-project-tester friction log` section present after both agents reported completion, with `context-evaluator`'s content missing until the lead manually reconstructed it as a `## Context-quality evaluation` section from that agent's task-notification summary); `planning/retros/phase-46-ledgerkit-tasks.md` "What didn't work" / "Lessons learnt" #1-2.
- **classification:** workflow
- **status:** promoted
- **recurrence:**
- **curation (Phase 46 triage, 2026-09-13, knowledge-curator):** provenance
  accepted — all required fields present; independently cross-checked
  against `planning/retros/phase-46-ledgerkit-tasks.md` ("What didn't
  work", "Lessons learnt" #1-2, "Process-improvement feedback") and
  against `planning/agent-led-workflow.md` step 5 itself, re-read
  directly rather than taken on the retro's characterization alone: step
  5 currently reads "**Delegate bounded specialist work.** One agent =
  one artifact. Give each a self-contained prompt (the phase plan path,
  exact scope, what to return). Run in the background unless the next
  step strictly depends on the result." — confirmed this says nothing
  today about two different specialist roles both contributing to one
  shared file, so this is a genuine, unaddressed gap in the doc's actual
  text, not a restatement of a rule that already covers the case. **Outcome:
  promote (recommendation + draft; does NOT land here — `agent-led-workflow.md`
  is outside this agent's write boundary, `planning/learnings/**` /
  `planning/context-gaps/**` / draft files under `planning/` only; the
  lead reviews and applies it, the same way L-013's step 10/14 split was
  handled).** Structurally the same shape as L-013 (Phase 44): a real,
  low-risk, specific process-doc gap, evidenced by one concrete incident
  with a real (not hypothetical) consequence already caught — worth
  closing now rather than waiting for a second silent race. Checked for a
  merge candidate: `L-006`/`L-013` are the only other workflow-classified
  candidates touching `agent-led-workflow.md`, and both are about
  roadmap/`CONTEXT.md` reconciliation *timing*, not about two agents
  writing one shared file — not a duplicate, a sibling gap in the same
  document. Checked whether this belongs in `context-gaps/` instead: no —
  per `context-gaps/README.md`'s own "what does NOT belong" list, this is
  a "how we should work" observation about the agent-led process itself,
  not a relationship CodeCompass's graph is missing; correctly stays in
  `planning/learnings/`.

  **Recommended fix — extend step 5** (draft, for the lead to review and
  land):

  > 5. **Delegate bounded specialist work.** One agent = one artifact. Give
  > each a self-contained prompt (the phase plan path, exact scope, what
  > to return). Run in the background unless the next step strictly
  > depends on the result. **If two different specialist roles must both
  > contribute to one shared report file, never dispatch both to `Write`
  > that path concurrently** — `Write` replaces the whole file, so
  > whichever call lands second always wins regardless of instructions to
  > "check the file's current state first," and the loss is silent: the
  > earlier agent's own success report gives no signal that its content
  > was later overwritten. Sequence them instead — one agent `Write`s the
  > file first, and only once its dispatch has fully completed is the
  > second told to `Edit`-append its section — or, if both must genuinely
  > run concurrently, give each its own file and merge them afterward
  > once both complete. (Phase 46 — L-018.)

  **Update (lead, same day):** the step-5 addition above has been applied
  to `planning/agent-led-workflow.md`, and `promoted.md` carries the
  matching `L-018 | 2026-09-13 | workflow | ...` pointer line — status
  updated to `promoted` accordingly, mirroring exactly how L-013 was
  closed out.
- **promoted_to:** `planning/agent-led-workflow.md` step 5 (concurrent-write
  guidance) — applied by the lead this phase, logged in `promoted.md`
  @ `329fa0a`.

### L-017 — a live WebFetch of an external reference manual is an expensive, unreliable fallback for section-specific technical content, distinct from whether CodeCompass should model manuals at all

- **origin:** Phase 46 (Ledgerkit genuine task — hledger 1.52 query-term
  semantics), lead's attempt + `reference-project-tester` verification
- **date:** 2026-09-13
- **project_revision:** b0717ee (codecompass) + ledgerkit `9c33e37`
- **observation:** after CodeCompass returned nothing (see `CG-002`) and
  Ledgerkit's own `dev-docs/planning/core-redefinition/07-query-regex.md`
  supplied a complete answer for all 6 query terms, the lead separately
  tried `WebFetch` against `https://hledger.org/1.52/hledger.html#queries`
  as a hypothetical fallback source. It correctly confirmed `acct:`/
  `desc:` (infix, case-insensitive regex) and `depth:` (top-N levels /
  `REGEXP=NUM` scoping) and `status:` (`status:`/`status:!`/`status:*`
  forms), but **two separate fetch attempts both failed to surface the
  page's AND/OR combination logic or the `not:` prefix documentation** —
  the manual page is long enough that a single fetch truncates before or
  around that section, and re-fetching didn't reliably target it. This is
  a distinct finding from "should CodeCompass index/relate the hledger
  manual" (already named as a hypothesis — `ledgerkit-plan.md` §1 item 2,
  `conditional-generalisation.md` §2.3, a future Stage D/E phase's own
  plan — number unresolved, Phase 53 was retargeted to legacy-feature
  rationalisation on 2026-09-14): it is evidence about the **cost profile
  of a live fetch specifically**, which bears directly on that future
  phase's open design question ("the hledger manual as fetched/vendored
  text") — a live per-question fetch of a large
  manual page is not a reliable substitute for a one-time
  fetched-and-indexed/vendored copy, independent of whatever schema Stage
  E eventually settles on for representing it.
- **evidence:** the lead's two `WebFetch` attempts against
  `hledger.org/1.52/hledger.html#queries` (both missing the AND/OR +
  `not:` section); Ledgerkit's own
  `dev-docs/planning/core-redefinition/07-query-regex.md` §7.1 already
  containing that exact information (negation row, implicit-AND/explicit-OR
  row) without needing any external fetch at all —
  independently re-read and confirmed by `reference-project-tester`
  (full table reproduced in
  `planning/reference-projects/ledgerkit/01-query-semantics.md`).
- **classification:** future-improvement
- **status:** retained
- **recurrence:** first occurrence
- **curation (Phase 46 triage, 2026-09-13, knowledge-curator):** provenance
  accepted — all required fields present; independently cross-checked
  against `planning/retros/phase-46-ledgerkit-tasks.md` ("What was
  achieved") and `planning/phase-47-consolidate-findings.md`'s own
  evidence inventory, which already names this candidate as Phase 47
  (GATE DB) bulk-review input. **Outcome: retain, not promote yet** —
  the same treatment `L-015`/`L-016` received at Phase 45's triage: real
  and specific, but single-occurrence (one lead attempt, two `WebFetch`
  calls) and explicitly the kind of finding Phase 47's consolidated bulk
  review is designed to weigh alongside the rest of the Phase 44-46
  evidence, not something a per-phase triage should pre-empt with a
  standalone promotion. Confirmed distinct from **CG-003**, per this
  candidate's own observation text: CG-003 is about whether CodeCompass
  should represent the manual at all (a graph-capability question, Stage
  E/GATE DD); this is about the retrieval-cost/reliability of a *live*
  fetch specifically, which bears on a future Stage D/E phase's "manual as
  fetched/vendored text" design question (number unresolved — see below)
  regardless of what Stage E eventually decides about representation. Not
  a merge candidate for either CG-003 or the already-named "should
  CodeCompass index the manual" hypothesis (`ledgerkit-plan.md` §1 item 2,
  `conditional-generalisation.md` §2.3) — those already have a home;
  this supplies one input to that question, not a duplicate of it.
  Checked for a prior related learning: none exists in this inbox
  (grepped for "WebFetch" — only this entry). Recommended destination
  once Phase 47's bulk review (or a second occurrence) acts on it: feeds
  that future Stage D/E phase's design question directly as one input
  among several, not a standalone `ROADMAP.md` row of its own (the design
  question already has a named home in that future phase's plan — number
  unresolved, Phase 53 was retargeted to legacy-feature rationalisation on
  2026-09-14). Revisit at Phase 47's bulk review.
- **promoted_to:** — (retained; feeds a future Stage D/E phase's design
  question via Phase 47's bulk review, no standalone destination)
- **curation (Phase 47 GATE DB bulk review, 2026-09-13, knowledge-curator):**
  confirmed out of scope for this gate, as this entry's own Phase 46
  triage anticipated: this is a retrieval-cost finding, not a
  detection-improvement or graph-capability decision, and it says nothing
  about what CodeCompass's own detection layer should do differently — it
  feeds a future Stage D/E phase's "manual as fetched/vendored text"
  design question directly (number unresolved — Phase 53 was retargeted
  to legacy-feature rationalisation on 2026-09-14;
  `planning/reference-projects/ledgerkit/findings.md` §5). No
  Stage C funding recommended for it. Status unchanged: `retained`.

### L-016 — `query relations`'s "not found" error is indistinguishable between "never scanned as a doc artifact" (a glob-coverage gap) and "genuine typo/misspelling" (real user error)

- **origin:** Phase 45 (Ledgerkit baseline, `context-evaluator`'s Q2 report — `planning/reference-projects/ledgerkit/00-baseline.md`)
- **date:** 2026-09-12
- **project_revision:** 6c3f34e (CodeCompass HEAD at baseline time)
- **observation:** `codecompass query relations dev-docs/hledger-compatibility.md` returns `error: 'dev-docs/hledger-compatibility.md' not found in context-graph.db` for a real, current file that is simply outside `spec_docs._DEFAULT_GLOBS` (the CG-002 root cause) — the exact same error message a genuine typo would produce. Traced through `src/codecompass/cli.py`: `_resolve_relations` returns `None` for both "never scanned as a doc artifact" and "path doesn't exist/is misspelled," and the CLI's `_not_found_error` can't distinguish them. This is a *symptom-layer* gap distinct from CG-002 (the glob list itself): even after CG-002 is fixed for `dev-docs/`, the identical ambiguity remains for the next unanticipated doc-directory convention the fixed glob list doesn't cover, and gives the caller zero signal to suspect a coverage gap rather than their own typo.
- **evidence:** `planning/reference-projects/ledgerkit/00-baseline.md` Q2 "Material gaps / failures" (second bullet) and "Criteria assessment" (Safety/trustworthiness: weak — "reads as an authoritative statement about what exists in the project, not a hedge"); `src/codecompass/cli.py::_resolve_relations`/`_not_found_error`; `src/codecompass/spec_docs.py::_DEFAULT_GLOBS`.
- **classification:** future-improvement
- **status:** promoted
- **recurrence:** first occurrence
- **curation (Phase 45 triage, 2026-09-13, knowledge-curator):** provenance
  accepted — all required fields present; independently re-traced
  `src/codecompass/cli.py::_resolve_relations`/`_not_found_error` and
  `spec_docs.py::_DEFAULT_GLOBS` (no `dev-docs/**/*.md` entry, confirming
  the CG-002 root cause this candidate builds on) rather than taking the
  baseline report's word alone. The claim stands: both "never scanned"
  and "genuinely doesn't exist" collapse into the identical
  `_not_found_error` string with no distinguishing signal. **Outcome:
  retain, not promote yet.** Real, specific, single-occurrence so far,
  and this candidate is explicitly named as Phase 46/47 input by
  `planning/v1-redefinition/roadmap.md`'s own Phase 47 description
  ("`knowledge-curator` reviews all Phase 45-46 candidate learnings…
  promotes anything with recurrence/evidence to a confirmed finding" —
  GATE DB). Promoting straight to a `ROADMAP.md` row now would pre-empt
  that consolidation step rather than feed it. Distinct from **CG-002**
  (retain that distinction explicitly, per this candidate's own
  observation text): CG-002 is the root-cause glob-coverage gap for
  `dev-docs/` specifically; this candidate is the *symptom-layer*
  ambiguity that outlives any individual glob fix — worth keeping
  separate rather than merging, since fixing CG-002 does not resolve
  this one. Recommended destination once Phase 47 or a second occurrence
  promotes it: a `future-improvement` `ROADMAP.md` row for a
  Stage-C-scale CLI fix — e.g. `_not_found_error` distinguishing "path
  exists on disk but was never scanned as a doc artifact" (say via
  `Path.exists()` before erroring) from "path does not exist at all",
  with a different message/hint for each (`roadmap-context-curator`
  finalises the row; lead/ad-hoc implementer lands the fix + a
  regression test once funded). Revisit at the Phase 47 bulk review or
  on a second reference-project instance of the same ambiguity.
- **promoted_to:** — (retained; revisit Phase 47 bulk review or on
  recurrence)
- **curation (Phase 47 GATE DB bulk review, 2026-09-13, knowledge-curator):**
  recurrence confirmed — this exact ambiguity was independently hit again
  in Phase 46's task 01 (`01-query-semantics.md`: both `dev-docs/`
  `query relations` calls returned the identical "not found" a typo would
  produce), the second occurrence since this candidate's own Phase 45
  filing. **GATE DB recommendation (full reasoning:
  `planning/reference-projects/ledgerkit/findings.md` §4/§7): bundle this
  fix with `CG-002`'s** — same root code path
  (`cli.py::_resolve_relations`/`_not_found_error`), same evidence base,
  cheap to fix together (distinguish "never scanned as a doc artifact"
  from "does not exist" before erroring). Status stays `retained`, not
  `promoted` — no artifact has landed; this is a recommendation for the
  lead/user to ratify at GATE DB, not yet implemented.
- **GATE DB ratified (lead, 2026-09-13):** user approved the
  recommendation as written. `planning/phase-49-spec-doc-coverage-and-error-disambiguation.md`
  now exists and scopes this fix alongside `CG-002`'s. Status stays
  `retained` until the fix actually lands in `src/codecompass/cli.py` —
  flips to `promoted` with a `promoted.md` line + commit hash at that
  point, per the same convention as `L-013`/`L-018`.
- **curation (Phase 49 closure, 2026-09-13, knowledge-curator):** fix
  confirmed landed — independently read `src/codecompass/cli.py` rather
  than taking the phase's own report on its word: `_relations_not_found_error`
  (L464-484) now exists, checks `(Path.cwd() / name).is_file()`, and on a
  hit prints "exists as a file but was not detected as a spec/vendor doc,
  so it has no relations recorded — check whether it's covered by
  spec_docs's glob coverage, then re-run sync" before exiting 1, falling
  through to the original bare `_not_found_error` otherwise;
  `query_relations` (L844) now calls it in place of the plain
  `_not_found_error` in its `relations is None` branch. Confirmed scoped
  precisely to `query relations` — `query_vendor`/`query_symbol`'s own
  not-found paths are untouched, correctly, since "does this path exist
  on disk" isn't a meaningful question for a vendor/symbol name.
  Regression coverage confirmed:
  `tests/test_cli.py::test_query_relations_unscanned_file_gets_disambiguated_error`
  (a real on-disk, unscanned file gets the new message, not "not found")
  and
  `tests/test_cli.py::test_query_relations_genuinely_nonexistent_name_keeps_not_found_message`
  (a name with no file on disk at all still gets the plain "not found",
  confirming the disambiguation doesn't over-fire). Also live-verified
  against the actual pinned Ledgerkit clone per
  `planning/phase-49-spec-doc-coverage-and-error-disambiguation.md`'s
  retro ("What was achieved" #4): a still-`dev-docs/`-uncovered real file
  (`knowledge/DOMAIN_RULES.md`) correctly triggers the new disambiguated
  message too, confirming the fix generalises rather than only covering
  the one directory (`dev-docs/`) it was evidenced against. **Status:
  `retained` → `promoted`**, per the convention already stated in the
  prior curation note. `promoted.md` line added this same triage.
- **promoted_to:** `src/codecompass/cli.py::_relations_not_found_error`
  + `tests/test_cli.py::test_query_relations_unscanned_file_gets_disambiguated_error`
  (+ `test_query_relations_genuinely_nonexistent_name_keeps_not_found_message`
  as the negative-case regression) @ `780e97b`.

### L-015 — `query vendors` / bare-discovery gives no signal that `[project.optional-dependencies]` exist but are unscanned

- **origin:** Phase 45 (Ledgerkit baseline, `context-evaluator`'s Q1 report — `planning/reference-projects/ledgerkit/00-baseline.md`)
- **date:** 2026-09-12
- **project_revision:** 6c3f34e (CodeCompass HEAD at baseline time)
- **observation:** Ledgerkit has `dependencies = []` (0 required runtime deps) but one real, tested, documented optional dependency (`pandas`, via `[project.optional-dependencies]`), which powers a real feature (`ledgerkit/_pandas_compat.py`, `tests/test_dataframe.py`, documented in 3 user-facing docs). `codecompass query vendors` and bare auto-discovery both correctly report "0 vendors" for the strict `dependencies` array, but neither emits any caveat that optional-dependencies exist in the manifest and are out of scope for discovery — confirmed deliberate scope (`discover_python()` in `src/codecompass/discovery.py` only reads `dependencies`, per `planning/phase-4-sync-index-init.md`), but the *silence at the CLI/query layer* about that scope boundary is what's evidenced here as gap-worthy, not the scope decision itself. An agent trusting "0 vendors" as "no dependency surface at all" would miss a real, shipped dependency.
- **evidence:** `planning/reference-projects/ledgerkit/00-baseline.md` Q1 (Verdict: PASS WITH GAPS; "Material gaps / failures"); `pyproject.toml`'s `[project.optional-dependencies]` block in the pinned Ledgerkit clone; `src/codecompass/discovery.py::discover_python()`.
- **classification:** future-improvement
- **status:** retained
- **recurrence:** first occurrence
- **curation (Phase 45 triage, 2026-09-13, knowledge-curator):** provenance
  accepted — all required fields present. Independently checked
  `src/codecompass/discovery.py::discover_python()`: it reads only the
  `dependencies` array, confirmed deliberate scope per
  `planning/phase-4-sync-index-init.md`, not a bug — the candidate itself
  already draws this distinction correctly (the gap is the *CLI/query
  layer's silence about the scope boundary*, not the scope decision).
  **Outcome: retain, not promote yet.** Real and specific, but
  single-occurrence and, like L-016, explicitly the kind of finding
  `planning/v1-redefinition/roadmap.md`'s Phase 47 (GATE DB) is designed
  to consolidate across Phases 45-46 before any roadmap commitment is
  made — promoting a lone Ledgerkit datapoint straight to a `ROADMAP.md`
  row now would jump ahead of that gate rather than feed it. Checked for
  a merge candidate: no prior learning about optional-dependency
  visibility exists in this inbox (grepped for
  "optional-dependencies"/`discover_python` — only this entry). Not a
  context-gap either — checked `planning/context-gaps/README.md`'s
  "what does NOT belong" list: this is a CLI-output-honesty gap about
  data CodeCompass already chooses not to scan, not a relationship the
  graph is missing, so it correctly stays in `planning/learnings/`, not
  `context-gaps/`. Recommended destination once Phase 47 or a second
  occurrence promotes it: a `future-improvement` `ROADMAP.md` row for a
  small CLI caveat — e.g. `codecompass query vendors` / the bare-discovery
  summary noting "N optional-dependency group(s) present in the manifest,
  out of scope for discovery" when `[project.optional-dependencies]` is
  non-empty but unused (`roadmap-context-curator` finalises the row).
  Revisit at the Phase 47 bulk review or on a second reference-project
  instance of the same silence.
- **promoted_to:** — (retained; revisit Phase 47 bulk review or on
  recurrence)
- **curation (Phase 47 GATE DB bulk review, 2026-09-13, knowledge-curator):**
  still single-occurrence — Phase 46's task 01 concerned query-term
  semantics, not the dependency-discovery code path this candidate is
  about, so it did not re-confirm it. Deliberately **kept out of** the
  narrow Stage C fix recommended for `CG-002`/`L-016`
  (`planning/reference-projects/ledgerkit/findings.md` §4): different code
  path (`discovery.py`, not `spec_docs.py`), and bundling an
  uncorroborated single-occurrence finding into an otherwise
  tightly-evidenced narrow phase would be scope creep. Status unchanged:
  `retained`; revisit at Phase 51's re-run or a second occurrence.
- **curation (Phase 51 closure, 2026-09-14, knowledge-curator):**
  independently re-read `planning/phase-51-rerun-ledgerkit-evaluation.md`'s
  own scope section and `planning/retros/phase-51-rerun-ledgerkit-evaluation.md`
  rather than assuming the commitment was honoured — confirmed Phase 51's
  actual scope was narrowly the two original FAIL cases (baseline Q2's
  `dev-docs/hledger-compatibility.md` lookup, task 01's query-term
  semantics) plus a generalisation check against a brand-new file
  (`17-query-semantics-brief.md`); none of those exercises
  `discovery.py::discover_python()` or Ledgerkit's
  `[project.optional-dependencies]` manifest section at all — a disjoint
  code path from what this candidate concerns, exactly as `findings.md`
  §4 anticipated when it deliberately kept this candidate out of Phase
  49's fix scope. Phase 51's own retro confirms no `src/codecompass/`
  change and no new candidate learnings were filed this phase (`retros/
  phase-51-*.md` "Time / cost note", "Candidate learnings filed"). So the
  §6 commitment ("revisit at Phase 51's re-run or a second occurrence")
  was not met by Phase 51 not because anyone skipped it, but because
  Phase 51 was scoped, correctly, to measure a different fix
  (`CG-002`/`L-016`) — it structurally could not have produced or
  refuted evidence about optional-dependency CLI silence one way or the
  other. **Outcome: stays `retained`, still single-occurrence, no new
  evidence from Phase 51's specific scope** — this is not a
  "no evidence after ~3 phases, default to discard" situation
  (`learning-lifecycle.md` §2), since the intervening phases (47, 49, 51)
  never had `discover_python()`/optional-dependency scanning in scope at
  all; the ~3-phase norm presumes phases that *could* have surfaced
  corroborating or disconfirming evidence and didn't, not phases that
  never touched the relevant code path. Revised revisit trigger, since
  "Phase 51's re-run" as originally written is now moot: **the next
  reference-project phase (Ledgerkit Stage D, a future reference project,
  or Technical Clipper) that actually exercises dependency discovery** —
  i.e. any task that runs `codecompass query vendors` or bare discovery
  against a project with a non-empty `[project.optional-dependencies]` (or
  equivalent) block — or a second, independent occurrence of the same
  silence, whichever comes first. If Stage D/Phase 52+ is never funded and
  no future reference project surfaces this again, this candidate should
  be revisited for a discard decision at that point on the same "no new
  evidence after ample opportunity" grounds `L-012` was just closed on
  below — not before, since it has not yet had a genuine opportunity.

### L-014 — a plan file's background/rationale claims can go stale between writing and implementation, independent of its scope list

- **origin:** Phase 44 (retro "Scope delivered vs planned" + "What didn't work" + "Lessons learnt" #1; `knowledge-curator` triage of the retro's contents per step 12)
- **date:** 2026-09-12
- **project_revision:** bf6db6e (current HEAD at triage time; Phase 44's own closeout commit is still pending)
- **observation:** `planning/phase-44-reference-project-protocol.md`'s scope section asserted the `context-evaluator`/`reference-project-tester` agent briefs had "placeholder method sections" left over from Phase 40 needing finalising. At implementation time, both briefs (`.claude/agents/context-evaluator.md`, `.claude/agents/reference-project-tester.md`) were found already fully fleshed out — no placeholder markers, no TODOs, already referencing the exact template filenames this phase was about to create — because Phase 43c had already updated them ("own / feed the new pathways"). No edit was needed; the plan's *background/rationale* claim (not its scope list, which was otherwise accurate) was simply stale by the time the phase ran. The phase behaved correctly here: it grepped for placeholder markers before touching anything, confirmed the claim was false, and recorded the deviation explicitly rather than either (a) blindly rewriting already-correct briefs to match a stale premise, or (b) silently treating "nothing to do" as unremarkable.
- **evidence:** `planning/phase-44-reference-project-protocol.md` line 38 ("finalise the `context-evaluator` and `reference-project-tester` agent briefs against these templates (they were created in Phase 40 with placeholder method sections)"); `planning/retros/phase-44-reference-project-protocol.md` "Scope delivered vs planned" and "What didn't work"/"Lessons learnt" #1 (independently re-read, not taken on the retro's word alone — the retro itself already cites the specific verification method used, grepping for placeholder markers, and names Phase 43c as the likely cause).
- **classification:** scoped-rule
- **status:** discarded
- **recurrence:** second occurrence merged here — `L-029` (Phase 62,
  2026-09-19): the plan's own claim that all three of
  `NpmAdapter`/`PythonAdapter`/`CargoAdapter` duplicated a walk+extract
  loop turned out wrong for `NpmAdapter` specifically; caught before any
  adapter file was edited, so still a "wasted-but-caught assumption,"
  not the "actually caused a wrong edit" case this entry's own curation
  note below reserved as the trigger for a stronger, independently-
  promotable candidate. Still discarded; revisit if a third occurrence
  appears, or if one actually reaches a shipped wrong edit.
- **curation (Phase 44 triage, 2026-09-12, knowledge-curator):** provenance
  accepted — both the plan file's claim and the retro's account of finding
  it stale are independently re-read and confirmed accurate. **Outcome:
  discard, not retain or promote.** This is the same shape as the
  declined companion candidate in L-008's Phase 43b triage: a
  single-occurrence, zero-harm instance of an *already-existing* project
  discipline working exactly as intended, not an unaddressed gap needing
  a new mechanism. `CLAUDE.md` §1 already requires a plan file per phase
  and pausing on unsettled assumptions; `agent-led-workflow.md`'s own
  opening line already states the governing discipline this instance
  demonstrates ("verify independently, every time, not just when
  something feels off"); step 1 of the 14-step workflow is literally
  "Inspect the repository" before proceeding. The phase did exactly
  that — grepped for placeholder markers, found the premise false,
  changed nothing, recorded the deviation — and nothing broke or was
  wasted. Filing a new scoped-rule for "verify a plan's background claims
  before acting on them" would be restating a norm this phase already
  correctly applied, not closing a gap it exposed. Distinguishing factor
  from a real retain-worthy candidate: no incorrect action was taken and
  no artifact needed correcting (contrast L-004/L-003, where the standing
  content itself was wrong and stayed wrong until a check existed).
  If a future phase's *background claim* being stale actually causes a
  wrong edit (not just a wasted-but-caught assumption), that would be a
  new, stronger candidate — not a recurrence of this one, since this one
  caused no harm.
- **promoted_to:** — (discarded; see rationale above)

### L-013 — the 14-step workflow's step 10 (roadmap/context reconciliation) can never satisfy its own "only if every DoD condition holds" clause at its listed position, since steps 11–13 (retro/triage/audit) haven't run yet

- **origin:** Phase 44 (retro "Process-improvement feedback"; `knowledge-curator` triage of the retro's contents per step 12)
- **date:** 2026-09-12
- **project_revision:** bf6db6e (current HEAD at triage time; Phase 44's own closeout commit is still pending)
- **observation:** `planning/agent-led-workflow.md` step 10 reads "flip the `ROADMAP.md` row *only if every DoD condition holds*" — but `CLAUDE.md` §5's Definition of Done requires a phase retro, a `knowledge-curator` triage, and a `release-phase-auditor` PASS to all exist before a phase counts as done, and none of those three exist yet at step 10's position in the list (they are steps 11, 12, and 13 respectively). So step 10, as literally sequenced, can never legitimately flip a row to `done` — its own stated condition is unsatisfiable at that point in the workflow. In practice, across this phase and at least two prior ones (43b, 43c, per this phase's own retro and cross-checked against `planning/retros/_audit-phase-43b.md` / `_audit-phase-43c.md`, both of which passed `release-phase-auditor` on the first round with the `ROADMAP.md` row still correctly held at "in progress" through step 10), the row has always actually flipped to `done` in a *second*, later `roadmap-context-curator` dispatch after steps 11–13 complete — never at step 10's own position. This is a standing ambiguity in the workflow doc's step ordering, not a new problem this phase caused: step 10's real job (as actually practiced) is a mid-phase `CONTEXT.md`/`CHANGELOG.md` update, and the final done-flipping reconciliation is a distinct, later action the doc doesn't currently name as its own step.
- **evidence:** `planning/agent-led-workflow.md` step 10 ("flip the `ROADMAP.md` row *only if every DoD condition holds*") vs. steps 11–13 (retro, triage, audit) listed *after* it; `CLAUDE.md` §5 (retro + triage + audit all required for done); `planning/retros/phase-44-reference-project-protocol.md` "Process-improvement feedback" (this phase's own account); `planning/retros/_audit-phase-43b.md` and `_audit-phase-43c.md` (both phases' `release-phase-auditor` passes confirming the `ROADMAP.md` row was correctly still "in progress" through their own step-10 runs, only flipped later).
- **classification:** workflow
- **status:** promoted
- **recurrence:** pattern observed across at least 3 phases (43b, 43c, 44) though this is the first time it was explicitly filed as a candidate rather than absorbed silently into practice
- **curation (Phase 44 triage, 2026-09-12, knowledge-curator):** provenance
  accepted — `agent-led-workflow.md`'s step 10/11/12/13 text and
  `CLAUDE.md` §5's DoD requirements independently re-read and confirmed
  to say what this candidate claims; the retro's account of prior-phase
  practice cross-checked against the two named audit files rather than
  taken on the retro's word alone. **Outcome: promote (recommendation +
  draft; not yet landed — `agent-led-workflow.md` is outside this
  agent's write boundary, `planning/learnings/**` /
  `planning/context-gaps/**` / draft files under `planning/` only).**
  This is real, specific, low-risk to fix (a clarifying edit, not a
  policy decision needing a gate), and has recurred silently across
  three phases without ever being named — worth closing now rather than
  waiting for a fourth silent workaround. Distinct from **L-006**
  (already promoted): L-006's fix is conditional — re-dispatch
  `roadmap-context-curator` *specifically when a retro changes the
  plan*. This candidate is unconditional — step 10's "flip to done"
  clause can never fire at its listed position *regardless* of whether
  the retro changes anything, because retro/triage/audit simply haven't
  happened yet. Not a duplicate; a sibling gap in the same document.
  **Recommended fix — split step 10 into an interim update and rename
  the final action explicitly, rather than renumber the whole list**
  (draft, for the lead to review and land):

  Step 10, reworded:
  > 10. **Reconcile roadmap and context state (interim).** Dispatch
  > `roadmap-context-curator`: overwrite `CONTEXT.md` and add the
  > `CHANGELOG.md` entry reflecting implementation + docs-audit progress
  > so far. **Do not flip the `ROADMAP.md` row to `done` here** —
  > `CLAUDE.md` §5's DoD requires the retro (step 11), triage (step 12),
  > and completion audit (step 13) to all exist first, and none of them
  > do yet at this point in the sequence. This step keeps `CONTEXT.md`
  > current mid-phase; it is not the phase's final reconciliation.

  Step 14, amended (append before "and move to the next phase"):
  > 14. **Refuse to mark work complete when the gate fails.** … Only on
  > `PASS` (or `PASS WITH NON-BLOCKING OBSERVATIONS`) does the lead
  > **re-dispatch `roadmap-context-curator` for the final
  > reconciliation** — flip the `ROADMAP.md` row to `done` now that every
  > DoD condition genuinely holds, and confirm `CONTEXT.md` reflects the
  > retro/triage/audit outcomes — then commit (`type(phase-N): summary`,
  > no AI attribution — `CLAUDE.md` §7) and move to the next phase.

  This preserves step 10's existing mid-phase value (an interim
  `CONTEXT.md`/`CHANGELOG.md` snapshot is genuinely useful if a session
  is interrupted between steps 10 and 13) while making explicit that the
  row-flip is a distinct, later action — matching what every phase has
  actually done in practice (per the audit-file cross-check above) rather
  than what the numbered list currently implies. Not landing this
  directly: `agent-led-workflow.md` is a core process doc outside this
  agent's write boundary, and — per the same caution `CLAUDE.md` §0
  applies to itself — a process-doc edit referenced by `CLAUDE.md` §8
  deserves the lead's explicit review before it's written, not a
  curator-authored fait accompli.
- **promoted_to:** `planning/agent-led-workflow.md` steps 10 + 14 —
  applied by the lead this phase, logged in `promoted.md` @ `3bd9257`.

### L-012 — single-symbol `query symbol` output undersells a vendor's actual usage breadth; `usage_count` isn't independently reproducible by grep

- **origin:** Phase 44 instrument dry-run (`planning/reference-projects/_instrument-dry-run.md`) — a self-test, not a real reference-project datapoint, but the observation is about CodeCompass's own query granularity, not about the target project, so it's filed here rather than discarded with the dry-run label.
- **date:** 2026-09-12
- **project_revision:** bf6db6e (pinned commit the dry-run evaluated at)
- **observation:** asking "what does this project use `typer` for" via `codecompass query symbol Typer --json` returns only the `Typer` class's own 2 call sites (`src/codecompass/cli.py:51`,`:54` — app construction). It omits that the large majority of the vendor's reported "usage count: 43" for `typer` as a whole is actually `typer.Option`/`Exit`/`Argument`/`confirm`/`Context` — the API surface that implements every CLI option, argument, exit code, and confirmation prompt. A reader trusting only the single-symbol query would undersell typer's role to "constructs two app objects." Separately, the vendor-level "usage count: 43" figure could not be exactly reproduced by direct `grep -oE "typer\.[A-Za-z_]+" src/codecompass/cli.py | sort | uniq -c` under any counting convention tried (grep-based counts landed 40–48 depending on what's included) — not demonstrably wrong, but not traceable to an exact provenance the way per-symbol `used_at` line citations are.
- **evidence:** `planning/reference-projects/_instrument-dry-run.md` (full report); `src/codecompass/cli.py` (option/argument/exit/confirm call sites); `codecompass query symbol Typer --json` output quoted in the report.
- **classification:** scoped-rule
- **status:** discarded
- **recurrence:** first occurrence (self-test, not a reference-project finding — see `context-quality-evaluation.md`'s "don't aggregate the dry-run" rule)
- **curation (Phase 44 triage, 2026-09-12, knowledge-curator):** provenance
  accepted and independently re-verified beyond taking the dry-run's word
  for it: re-ran the same `typer\.[A-Za-z_]+` pattern directly against
  `src/codecompass/cli.py` — 40 total occurrences, breaking down to
  `Typer` ×2 (L51, L54), `Option` ×17, `Exit` ×13, `Argument` ×5,
  `confirm` ×2, `Context` ×1, matching the dry-run's own per-symbol
  breakdown exactly. **Outcome: retain, not promote (yet).** Two distinct
  findings bundled in one candidate:
  1. *Single-symbol query undersells breadth* — this is a genuine
     product-quality observation (`query symbol <X>` only ever returns
     `<X>`'s own call sites, never sibling members of the same vendor
     used in the same file/feature), but it comes from a single
     self-test explicitly labelled "not a real datapoint" and "do not
     aggregate into Phase 47/62-63 findings" by the phase's own plan and
     the dry-run report's own header. Promoting a self-test finding
     straight to a `ROADMAP.md` row would treat it as more authoritative
     than the phase design intended. The phase's own retro reaches the
     same conclusion independently ("its one gap … is exactly the kind
     of evidence Stage C (GATE DB) exists to weigh, not something to
     react to now" — "Where we're going", trajectory confirmed).
     Checked `planning/context-gaps/README.md`'s "what does NOT belong"
     list before considering it a context-gap instead: "feature requests
     for `query` output formatting" are explicitly excluded there, and
     this is exactly that — the underlying data (`Option`/`Exit`/etc.
     usage) already exists in the graph; nothing is *missing* from
     `context-graph.db`, a query's *scope* is just narrow. Confirmed
     staying in `planning/learnings/`, not filed as a `context-gaps/`
     entry too.
     Also checked `conditional-generalisation.md` §1.2's hypothesis table
     for a fit: none of the six rows (technical-dependency concept,
     executable kind, spec/manual kind, provenance, browser-API kind,
     task-oriented retrieval edges) match a same-vendor sibling-symbol
     query-scope gap — this doesn't currently feed any named GATE DB/DD
     hypothesis, it would be a new one if it recurs.
  2. *`usage_count` not exactly grep-reproducible* — independently
     confirmed the count is in the right ballpark (this repo's own
     `typer\.` pattern count is 40 in `cli.py` alone, consistent with the
     dry-run's own reconciliation of "43" once test-file mentions and
     `typer.testing.CliRunner` imports are added) and not demonstrably
     wrong, just not traceable to one exact documented convention. Not
     enough on its own to justify an invariant/test today — there's no
     evidence the count is *incorrect*, only that its provenance isn't
     externally auditable the way per-symbol `used_at` citations are.
  Recommended destination, once either half recurs on a real
  reference-project evaluation (Ledgerkit, Phase 45+) or survives to the
  Phase 47 bulk review: (1) a `future-improvement` `ROADMAP.md` row —
  "`query symbol`/`query vendor` should surface or link sibling API
  members of the same vendor used in the same file, not just the queried
  symbol's own call sites" (`roadmap-context-curator` finalises); (2) a
  short `docs/` note documenting `usage_count`'s exact computation so it
  is independently auditable (`docs-maintainer` finalises), if a second
  instance shows the ambiguity actually misleads someone rather than
  merely being unreproducible-by-grep. Revisit at Phase 45's real
  Ledgerkit evaluation, the Phase 47 bulk review, or on a second
  self-test/reference-project instance of either finding.
- **promoted_to:** — (retained; revisit Phase 45/47 or on recurrence)
- **curation (Phase 47 GATE DB bulk review, 2026-09-13, knowledge-curator):**
  still uncorroborated by any real reference-project finding — remains a
  self-test-only observation, explicitly excluded from aggregation by its
  own phase's design
  (`planning/v1-redefinition/context-quality-evaluation.md` doesn't
  count dry-runs), and no Ledgerkit task has touched `query symbol`
  scope. Now 3 phases old (filed Phase 44, no new evidence through Phase
  47) — flagged per the lifecycle's own "~3 phases without new evidence
  is a discard candidate" norm (`learning-lifecycle.md` §2), though not
  forced since its status is `retained` rather than `evidence-gathering`.
  **Recommendation: revisit at Phase 51's re-run; discard if still
  uncorroborated by then** rather than carrying it indefinitely. Full
  reasoning: `planning/reference-projects/ledgerkit/findings.md` §6.
- **curation (Phase 51 closure, 2026-09-14, knowledge-curator):**
  independently re-read `planning/phase-51-rerun-ledgerkit-evaluation.md`'s
  scope and `planning/retros/phase-51-rerun-ledgerkit-evaluation.md`
  rather than assuming the promised re-evaluation happened — confirmed
  Phase 51 was scoped narrowly to re-running baseline Q2 and task 01 (the
  two original FAIL cases) plus a generalisation check on
  `17-query-semantics-brief.md`; none of that exercises `query symbol`
  against any vendor, single or multi-member, so this candidate's domain
  (single-symbol query-scope breadth) got no opportunity to be
  corroborated or refuted this phase either — structurally the same
  situation as `L-015` above, confirmed by the same source documents.
  However, this candidate is treated differently from `L-015`, because
  the difference between them is real, not just symmetric bad luck:
  `L-015`'s domain (`discovery.py`'s optional-dependency scanning) has
  never once been in scope for *any* phase since its Phase 45 filing —
  Phase 46 was query semantics, Phase 49 was the glob/error-message fix,
  Phase 51 was the re-run of those two — so it has had zero genuine
  opportunities. `L-012`'s domain, by contrast, *was* filed against a
  standing gap that Ledgerkit's own reference-project evaluations have
  now had two full baseline/task rounds (Phases 45-46) plus a re-run
  (Phase 51) to potentially exercise, and none of the questions asked at
  any of those rounds happened to probe `query symbol`'s single-symbol
  scope specifically — not because the domain is inherently untestable
  the way `L-015`'s is unless a future task deliberately targets
  optional-dependencies, but because no evaluator or task designer across
  three real evaluation rounds has picked a question shaped like "what
  does this project use vendor X for" that would exercise it. That is a
  meaningfully weaker basis for continued waiting: this is now **7 phases
  since filing (44→51)** with the specific self-test-only caveat
  (`context-quality-evaluation.md`'s "don't aggregate the dry-run" rule)
  still unlifted by a single real reference-project instance, and Phase
  47's own bulk review already named this exact re-run as the forcing
  function for a promote/discard decision rather than another deferral
  (`findings.md` §6, quoted above) — explicitly not open-ended.
  Re-checked for a merge/promote path before defaulting to discard: no
  second self-test or reference-project instance of either bundled
  finding (single-symbol breadth undersell; `usage_count` non-grep-
  reproducibility) has surfaced anywhere in `inbox.md`, `promoted.md`, or
  any Ledgerkit evaluation file since Phase 44 (re-grepped for
  "query symbol"/"usage_count" across `planning/reference-projects/` —
  no hits outside this candidate's own origin document and Phase 44's
  triage). Per `learning-lifecycle.md` §2's explicit norm — "a candidate
  with no new evidence after ~3 phases is a discard candidate (curator's
  call)" — and given this task's own instruction not to defer a third
  time, **outcome: discard, not retain further.** This is not a claim the
  underlying observation is false (code-level re-verification at Phase
  44's own triage already confirmed the `typer.Option`/`Exit`/`Argument`/
  `confirm`/`Context` breakdown is accurate); it is a claim that a
  self-test-only finding with three real reference-project opportunities
  to corroborate and zero takers has exhausted the lifecycle's patience
  for "retained, awaiting evidence" and should not be carried a fourth
  time on the same uncorroborated basis. If a future reference-project
  task (Ledgerkit Stage D, Technical Clipper, or elsewhere) independently
  hits the same single-symbol-undersells-breadth shape, it should be
  filed as a **new** candidate learning citing that real instance as its
  origin — not a reopening of this one — since the discard reason here is
  "no real-world corroboration despite ample opportunity," not "this
  phenomenon doesn't occur."
- **promoted_to:** — (discarded; see Phase 51 closure rationale above)

### L-011 — `check_generated_artifacts_match_source`'s SKILL.md branch false-positives on any environment without a synced `context-graph.db` (a fresh clone/checkout/CI runner)

- **origin:** fresh-Pi dev-environment setup audit, reported by
  `roadmap-context-curator`, triaged by `knowledge-curator`
- **date:** 2026-09-12
- **project_revision:** af05987 (current HEAD at triage time)
- **observation:** on a genuinely fresh checkout (new venv, `pip install
  -e '.[dev]'`, no `codecompass sync` ever run against this repo — so
  neither `context-graph.db` nor `vendor/` exist, both gitignored),
  `pytest` fails two tests:
  `tests/test_check_user_docs.py::test_no_false_positives_against_real_repo`
  and
  `tests/test_check_user_docs.py::TestGeneratedArtifactsMatchSource::test_clean_against_real_repo`.
  Root cause: `render_tool_skill()` (`src/codecompass/skill.py:36-57`)
  correctly and deliberately degrades to `enriched_count = 0` / every
  vendor `no` when `context-graph.db` doesn't exist yet (its own
  docstring: "`False` for every vendor if `context-graph.db` doesn't
  exist yet, rather than erroring") — but the committed
  `.claude/skills/codecompass/SKILL.md` (`.claude/skills/codecompass/SKILL.md:28`)
  says "4 tracked, 3 enriched" because it was generated on a machine that
  had already run `codecompass sync`. `check_generated_artifacts_match_source`
  (`scripts/check_user_docs.py:701-764`, added Phase 43b, motivated by
  L-005) byte-diffs the committed file against a fresh call to
  `render_tool_skill` with no guard for "`context-graph.db` doesn't exist
  at `root`" — unlike its own sibling branch two lines up, which already
  degrades gracefully ("could not import codecompass … skipped", L715-723)
  when `src/` isn't importable. The function's own docstring claims it's
  "deliberately narrow: only the two artifacts a bare function call can
  reproduce **without a live sync**" (L708-712) — false today for the
  enrichment portion of `SKILL.md` specifically, which *is*
  sync-state-dependent. `CONTRIBUTING.md`'s documented dev setup
  (`CONTRIBUTING.md:165-171`: `pip install -e ".[dev]"` / `pytest` /
  `ruff check .`) never mentions `codecompass sync`, so any genuinely
  fresh clone (new contributor, new CI runner, new dev machine) hits
  these 2 failures out of the box with no documented fix.
- **evidence:** `src/codecompass/skill.py:23-57`
  (`_open_graph_readonly`/`render_tool_skill`); `.claude/skills/codecompass/SKILL.md:28-35`
  (committed "3 enriched" state); `scripts/check_user_docs.py:701-764`
  (`check_generated_artifacts_match_source`, no `context-graph.db`
  existence guard on the SKILL.md branch, contrast with its own
  `generators is None` graceful-degrade branch at L715-723);
  `tests/test_check_user_docs.py:23-25` and `:458-459` (the two failing
  tests, no fixture/skip keyed on `context-graph.db`); confirmed no
  `tests/conftest.py` exists and no `skipif`/`xfail` anywhere in `tests/`
  addresses this; `CONTRIBUTING.md:165-171` (no `sync` step);
  `.gitignore:32,36` (`vendor/`, `context-graph.db` both gitignored, so a
  fresh clone genuinely lacks both). Checked and **rejected** "just
  document `codecompass sync` as a required bootstrap step" as the
  primary fix: `src/codecompass/enrichment.py`'s disclosed
  cost-estimate/budget gate confirms `sync` on this repo's own
  already-usage-proven `vendor.toml` auto-triggers real, API-key-gated,
  cost-incurring AI enrichment calls — a bad prerequisite to impose on
  every fresh contributor or CI runner just to get `pytest` green.
- **classification:** invariant (the check's own false-positive-free
  operation on an environment with no synced graph is a required
  property it currently violates — same *shape* of gap as L-008
  ("a prose/text-matching check needs its false-positive test before its
  true-positive one"), but for a *generated-artifact-diff* check rather
  than a prose-pattern-match check, and from the same Phase 43b batch as
  L-005's invariant half. Not merged with L-008 — different check,
  different failure mechanism (environment/sync-state, not prose
  content) — but noted as a sibling instance of "a Phase 43b
  drift-detection check shipped without a false-positive case for the
  one environment state its own inputs can legitimately take.")
- **status:** promoted
- **recurrence:** first occurrence
- **curation (fresh-Pi triage, 2026-09-12, knowledge-curator):**
  provenance accepted and independently re-verified line-by-line (see
  evidence) — this is real, specific, reproducible, and not previously
  filed (checked `inbox.md`, `promoted.md`, `CONTEXT.md`, and
  `planning/retros/phase-43b-standing-doc-drift-checks.md`: none mention
  a fresh-checkout/no-synced-graph failure mode for this check).
  **Outcome: promote-recommendation** (not yet promoted — no artifact has
  landed). This blocks a basic contributor/CI workflow
  (`pip install -e ".[dev]"; pytest`) with no documented workaround, so
  it shouldn't sit as merely "retained." Recommending a concrete
  destination + draft rather than leaving it open-ended:
  - **Preferred fix (invariant → test, `scripts/check_user_docs.py` +
    `tests/test_check_user_docs.py`, lead/ad-hoc implementer finalizes):**
    make the SKILL.md branch of `check_generated_artifacts_match_source`
    skip the comparison — an informational, non-strict `Finding`
    ("`context-graph.db` not found — skipped SKILL.md enrichment-status
    comparison; run `codecompass sync` to verify fully"), mirroring the
    existing `generators is None` degrade pattern at L715-723 — whenever
    `(root / "context-graph.db").exists()` is `False`. Pair it with a new
    regression test in `TestGeneratedArtifactsMatchSource` (sibling to
    the existing `test_missing_artifacts_produce_no_finding`, L461-463):
    a fixture with a committed SKILL.md saying "3 enriched" but *no*
    `context-graph.db` present, asserting `findings == []` (or only the
    informational non-strict finding) rather than a drift flag. This
    keeps the check's real purpose intact (still catches a genuine hand
    edit or generator change on a machine that *does* have a synced
    graph) without penalizing the no-graph-yet state the generator itself
    treats as legitimate.
  - **Rejected alternative A:** document `codecompass sync --yes` as a
    required `CONTRIBUTING.md` bootstrap step before `pytest` — rejected
    as the *primary* fix because it makes a real, API-key-gated,
    cost-incurring AI call a prerequisite for running the unit test
    suite (see evidence). Could still be a *secondary*, clearly-labeled
    "optional: if you want `.claude/skills/codecompass/SKILL.md` to
    reflect real enrichment state locally, run `codecompass sync`" note,
    but that's polish, not the fix for the failing tests.
  - **Rejected alternative B:** commit a `SKILL.md` generated in the
    "0 enriched" state instead — rejected because it doesn't fix
    anything structurally; it just flips which environment the check
    disagrees with (a normal dev machine that *has* run `sync`, which is
    this project's own ordinary dogfooding state, would then fail the
    same check the other way, and the next real `codecompass index` run
    would regenerate "3 enriched" and reintroduce the mismatch
    immediately).
  - Not the curator's place to land either the check/test change or a
    `CONTRIBUTING.md` note — both are `scripts/`/`tests/`/`CONTRIBUTING.md`
    edits outside this agent's write boundary (`planning/learnings/**`,
    `planning/context-gaps/**`, draft files under `planning/` only).
- **promoted_to:** `scripts/check_user_docs.py::check_generated_artifacts_match_source`
  + `tests/test_check_user_docs.py::TestGeneratedArtifactsMatchSource::test_skill_comparison_skipped_without_graph_db`
  @ `80162fd` — the curator's preferred fix: the SKILL.md branch now
  skips with an informational, non-strict `Finding` when
  `(root / "context-graph.db").is_file()` is `False`; the two real-repo
  assertions (`test_no_false_positives_against_real_repo`,
  `test_clean_against_real_repo`) were narrowed from `findings == []` to
  `[f for f in findings if f.strict] == []` since an informational
  finding is expected on any unsynced checkout and never fails
  `--strict` anyway (`Finding.strict`); a new regression test covers the
  skip path. Full suite (554 passed, 2 skipped) + `ruff check` verified
  green on this fresh Pi environment before committing.

### L-010 — a reusable/exported document is stronger when it cites the specific incident behind each recommendation and states its own revision policy up front

- **origin:** Phase 43e (`adoption-blueprint.md`; retro "Lessons learnt"
  #1 and #2)
- **date:** 2026-09-12
- **project_revision:** e2f7122 (current HEAD at triage time; the 43d/43e
  planning-doc changes — `licence-migration.md`, `adoption-blueprint.md`,
  `decisions/0052`/`0053` — are this session's uncommitted work, not yet
  in a closeout commit)
- **observation:** `planning/v1-redefinition/adoption-blueprint.md` — a
  document explicitly written to be handed to a *different* project
  (Ledgerkit) and later revised from its real adoption experience (§10) —
  uses two authoring techniques its own retro identifies as load-bearing
  for that kind of document specifically: (1) recommendations cite the
  concrete CodeCompass phase/incident that justified them rather than
  reading as generic agent-led-development advice (e.g. §0's
  `[CODECOMPASS-GENERATED]` tag names Phase 43b's
  `check_generated_artifacts_match_source` explicitly as "a real
  incident, not a hypothetical"; §7 names Phases 41/42/43/43b/43c as the
  phases `release-phase-auditor` caught a real gap in); (2) §10 states,
  before any external party has actually used the document, that it is
  "deliberately not treated as finished on first write" and schedules its
  own revision (Phase 55/GATE DD). Both are reusable techniques for *any
  future CodeCompass-authored document meant for consumption outside this
  repository or as a template* — not specific to this one blueprint.
- **evidence:**
  `planning/retros/phase-43e-agent-led-adoption-blueprint.md` "Lessons
  learnt" #1 and #2;
  `planning/v1-redefinition/adoption-blueprint.md` §0 (the
  `[CODECOMPASS-GENERATED]` tag citing Phase 43b), §7 (naming Phases
  41/42/43/43b/43c), §10 ("Revision policy").
- **classification:** scoped-rule
- **status:** retained
- **recurrence:** first occurrence
- **curation (Phase 43d+43e triage, 2026-09-12, knowledge-curator):**
  provenance accepted — both retro lessons and all three cited
  `adoption-blueprint.md` sections exist and say what this candidate
  claims (independently re-read, not taken on the retro's word alone).
  **Outcome: retain**, not promote. Real and specific, but single
  occurrence and no clean destination agent today — this document lives
  under `planning/v1-redefinition/`, which no specialist agent owns the
  way `docs-maintainer` owns `docs/`/`architecture/` (the lead writes it
  directly). Checked `codecompass-feedback-ingestion.md` (the other
  reusable/exported document written this same session) as a possible
  second instance: it partially matches — it cites the concrete
  documents/decisions it's built from (`context-quality-evaluation.md`,
  `reference-project-protocol.md` §2.6, `decisions/0051`) rather than
  reading as generic advice — but it has no explicit "this is not
  finished on first write" revision-policy section, so it isn't a clean
  second occurrence of *both* techniques. Not counted as recurrence.
  Plausible destination once/if a second instance is needed: a short
  authoring note wherever future reusable/exported planning documents get
  written — `planning/agent-led-workflow.md` or
  `planning/v1-redefinition/documentation-lifecycle.md` are the two
  candidate homes, decided at that time. Revisit when
  `adoption-blueprint.md` is actually revised (Phase 55/GATE DD, per its
  own §10) or when CodeCompass next authors a document meant for
  cross-project or template use.
- **promoted_to:** — (retained; no destination artifact yet, revisit
  Phase 55/GATE DD or on a second reusable-document instance)
- **addendum (Phase 45 triage, 2026-09-13, knowledge-curator):** mining
  Phase 45's retro (`planning/retros/phase-45-ledgerkit-baseline.md`,
  "Lessons learnt" #3 + "What was achieved") turned up a first real-world
  adoption signal for the document L-010 concerns:  Ledgerkit has
  independently stood up a `.claude/agents/context-curator.md` role and a
  `validation/codecompass/` findings-intake mechanism, structurally
  matching `codecompass-feedback-ingestion.md` almost exactly, discovered
  incidentally while reading Ledgerkit's repo for an unrelated reason
  (its Stage A closeout note) rather than sought out — with zero findings
  filed yet. Considered filing this as a new standalone candidate;
  **declined** — it isn't itself a "how we should work" observation the
  way L-010's own two authoring techniques are, it's a fact about another
  project's behaviour, and it's already captured durably in
  `planning/reference-projects/ledgerkit.md` (the registration record)
  and this phase's own retro, so a third copy in `planning/learnings/`
  would be restating rather than adding. Filed here instead, as a
  cross-reference: this is exactly the kind of evidence L-010's own
  "revisit… when CodeCompass next authors a document meant for
  cross-project or template use" trigger anticipates, and it strengthens
  (without yet satisfying) the case for `adoption-blueprint.md`'s
  scheduled Phase 55/GATE DD revision — an adopting project's real usage,
  not just CodeCompass's own authoring intent, will be available to
  revise against by then. Status unchanged (**retained** — no revision
  has happened yet, only adoption).

### L-009 — fetching externally-authoritative text (e.g. licence text) directly from its own canonical source guarantees byte-fidelity that memory/a template can't

- **origin:** Phase 43d (GPL-3.0-or-later relicensing; retro "What
  worked" #1 and "Lessons learnt" #2)
- **date:** 2026-09-12
- **project_revision:** e2f7122 (current HEAD at triage time; `LICENSE`,
  `pyproject.toml`, `decisions/0052`/`0053` are this session's
  uncommitted work, not yet in a closeout commit)
- **observation:** `LICENSE`'s new GPL-3.0-or-later text was fetched
  directly from `hledgerorg/hledger`'s own `LICENSE` file via `gh api`,
  rather than retyped or reconstructed from training-data memory of "the
  GPL text" — per the FSF's own instruction that licence text must not be
  modified, and specifically because this relicensing's whole stated
  purpose (`licence-migration.md` §1) is alignment with hledger's own
  licence family, so verified byte-parity with hledger's actual file is
  stronger evidence than "this is probably the same GPL text everyone
  uses." This is the same underlying discipline the project already
  applies to vendored dependencies (root `CLAUDE.md`'s vendor table:
  "Consult the linked digest before relying on training knowledge";
  `.claude/skills/codecompass-{rich,typer,anthropic}/SKILL.md`: "retrieved
  from its own upstream repository — not from training knowledge") but
  applied here to a different artifact class (legal/licence text, not a
  library API) and with no existing mechanism enforcing it for that
  class.
- **evidence:**
  `planning/retros/phase-43d-gpl-relicensing-plan.md` "What worked" #1
  and "Lessons learnt" #2; `planning/v1-redefinition/licence-migration.md`
  §3 ("Replace MIT text with the canonical GPL-3.0-or-later `COPYING`
  text… the FSF's own instructions: use the license text verbatim,
  unmodified"); `CLAUDE.md`'s vendor table caution as the existing analog
  for a different artifact class.
- **classification:** scoped-rule
- **status:** retained
- **recurrence:** first occurrence
- **curation (Phase 43d+43e triage, 2026-09-12, knowledge-curator):**
  provenance accepted — retro text, `licence-migration.md` §3, and the
  vendor-table analog all independently re-read and confirmed. **Outcome:
  retain**, not promote. Real and a genuinely reusable discipline (fetch
  canonical text live rather than trust memory, whenever byte-exactness
  with a specific external source is the actual point), but this
  particular instance — relicensing — is a single, already-completed,
  not-currently-recurring event; no future phase is scheduled to touch
  `LICENSE` again. No clean destination agent either: editing `LICENSE`
  is the lead's own direct action, not a specialist-agent's remit, so
  there is no `.claude/agents/*.md` brief to amend today. Plausible future
  destination if this recurs: a short line in
  `CONTRIBUTING.md`/`CLAUDE.md`'s vendor-table section or the ADR-proposal
  guidance generalising "fetch canonical text for byte-fidelity" beyond
  vendored dependencies to any externally-authoritative text a future
  change incorporates (a licence, a copied upstream spec fragment quoted
  in an ADR, etc.). Revisit if a second such incident occurs (another
  relicensing, a future vendor-licence audit, or an ADR that needs to
  quote external text verbatim).
- **promoted_to:** — (retained; no destination artifact yet, single
  occurrence, revisit on recurrence)

### L-008 — a prose/text-matching check needs its false-positive regression tests before its true-positive one

- **origin:** Phase 43b (`check_no_deleted_names_as_live`'s first design
  iteration; retro "What didn't work" #1 + Lesson 1)
- **date:** 2026-09-11
- **project_revision:** `<Phase 43b commit>`
- **observation:** the first implementation of
  `check_no_deleted_names_as_live` used a naive "flag any line containing
  a retired name" heuristic and produced ~30 false positives when run
  against this repo's own real docs (which legitimately discuss retired
  concepts historically at length — exactly the failure mode L-003/L-004's
  own description of the problem already implied). The design was
  iterated to prose-unit matching with a historical-marker vocabulary,
  calibrated until a manual run produced zero false positives, *before*
  any regression test was written. The false-positive-shaped tests
  (`test_does_not_flag_historically_framed_mention`,
  `test_ignores_fenced_code_examples`) were written after the design
  settled, not before, so the ordering wasn't literally
  false-positive-test-first — but the manual-testing equivalent of that
  discipline (test against false positives before against true positives)
  is what caught the flaw cheaply, in minutes, rather than in a later
  audit round. This is a reusable authoring discipline for *any future
  check that pattern-matches over prose* (not just this one) — including,
  plausibly, Stage C's mechanical-detection heuristics for context gaps
  (`planning/context-gaps/`), which will also be text/pattern matching
  over code/docs and share the same false-positive risk shape.
- **evidence:** `planning/retros/phase-43b-standing-doc-drift-checks.md`
  "What didn't work" #1 and Lesson 1 ("A 'detect stale/retired content'
  check needs a false-positive test suite before its true-positive
  one"); `tests/test_check_user_docs.py::TestNoDeletedNamesAsLive`
  (`test_does_not_flag_historically_framed_mention` L397,
  `test_ignores_fenced_code_examples` L418) as the landed artifact
  demonstrating the calibrated design.
- **classification:** project-rule
- **status:** retained
- **recurrence:** first occurrence
- **curation (Phase 43b triage, 2026-09-11, knowledge-curator):**
  provenance accepted — the retro text and the named tests both exist as
  cited. **Outcome: retain**, not promote. Real and specific, with a
  plausible destination (a short authoring note in
  `.claude/skills/docs-sync/SKILL.md`, which already lists both Phase 43b
  checks as items 13-14: "when adding a new `check_user_docs.py` rule
  that pattern-matches over prose, write and run the false-positive case
  — 'does this fire on content that is correctly discussing the matched
  term historically/in a code example' — before writing the true-positive
  regression test; a naive first design commonly over-fires on exactly
  this project's own history-narrating docs, per
  `check_no_deleted_names_as_live`'s first iteration") — but single
  occurrence, and the curator has no write access to `.claude/skills/`
  (outside `planning/learnings/**`/`planning/context-gaps/**`/draft files
  under `planning/`) to land it directly. Not promoted until either (a)
  the lead/`docs-maintainer` adds the note and a commit exists to log
  here, or (b) a second prose-matching check hits the same false-positive
  trap, at which point recurrence makes the case stronger. Considered and
  **declined to file** a second candidate for the retro's other "what
  didn't work" item (the plan's retired-names list being factually
  imprecise, `_RAW_TEXT_CHAR_CAP`/`_DOCS_FILE_CAP` surviving): that item
  is not a gap needing a new mechanism — it's a single-occurrence
  successful application of an *already-existing* project discipline
  ("verify against `src/`, not the candidate's prose", which the retro
  itself notes the `_iter_learning_candidates`/ADR-cross-reference checks
  already model) catching an error before it landed. Filing a learning
  for a discipline that already exists and worked as intended would be
  filing to have filed one, not because there's an unaddressed gap.
- **promoted_to:** — (retained; destination is a `docs-sync/SKILL.md`
  authoring note, pending lead action or recurrence)

### L-007 — a plan's "Done when" should separate "the mechanism exists" from "the mechanism has produced output"

- **origin:** Phase 43c (retro lesson 2 + "what didn't work" #2;
  `knowledge-curator` triage)
- **date:** 2026-09-11
- **project_revision:** f47f3e2 (Phase 43c plan commit)
- **observation:** Phase 43c's plan Verification said the
  `context-health-planner` agent "runs once for real and produces the
  `context-health.md` above". The agent was *created* this phase, so the
  lead wrote the first `context-health.md` by hand (running the same
  `codecompass query` commands) and the agent's first genuine solo run
  slipped to before Phase 45. "An agent will own X" and "X has been
  produced by that agent this phase" are different commitments; a plan
  that conflates them lets an artifact land with a stubbed first
  datapoint and no gate catching the gap. Same shape as the same plan's
  §2 over-scoping (it predicted three `conditional-generalisation.md`
  edits; one was needed).
- **evidence:** `planning/phase-43c-agent-context-pathways.md`
  Verification vs. `planning/retros/phase-43c-agent-context-pathways.md`
  "What didn't work" #2 and "Where we're going" (agent's first real run
  deferred to before Phase 45); `planning/context-health.md`'s first
  assessment is lead-written narrative, not an agent report.
- **classification:** workflow
- **status:** retained
- **recurrence:** first occurrence (the §2 over-scoping item in the same
  retro is a weaker related instance of plan-estimate imprecision)
- **curation (Phase 43c triage, 2026-09-11, knowledge-curator):**
  provenance accepted — both sources are this phase's own plan + retro,
  cross-checked against `planning/context-health.md` (first assessment is
  lead narrative, no agent header). **Outcome: retain.** Real and
  specific but single-instance and not yet actionable; the candidate
  destination is a one-line addition to the plan-file guidance (CLAUDE.md
  §1 / the `agent-led-workflow.md` step-1 plan template: "Done-when
  distinguishes 'the mechanism exists' from 'the mechanism has produced
  output this phase'"). That is a CLAUDE.md-class change and needs
  recurrence evidence before it is worth proposing via
  `planning/v1-redefinition/proposed-governance-changes.md`. Revisit at
  the Phase 47 bulk review or on the next occurrence.
- **promoted_to:** — (retained; revisit Phase 47 or on recurrence)

### L-006 — the curator reconciles *before* the retro, but a GATE/retro can change the plan

- **origin:** Phase 43 (dogfood; `release-phase-auditor` FAIL ×3 on
  planning-doc bookkeeping)
- **date:** 2026-09-10
- **project_revision:** d34a486
- **observation:** the 14-step workflow runs `roadmap-context-curator`
  (step 10) *before* the lead writes the retro (step 11). For most phases
  that's fine. But a **GATE phase** (or any retro that schedules a
  follow-up phase or records roster amendments) *changes the roadmap*
  after step 10 — so the curator's reconciliation is already stale when
  it lands. Phase 43's `release-phase-auditor` FAILed 3 times, entirely
  on planning-doc bookkeeping the lead then hand-patched piecemeal
  (missing `43b` ROADMAP row — `phase-43b` was created after the curator
  ran; `v1-redefinition/roadmap.md` GATE DA outcome — the curator read
  "roadmap.md" as `ROADMAP.md`; `43b` absent from the CONTEXT forward
  path — written before the retro existed; then the CONTEXT fix left the
  file self-contradictory). The lead is a poor substitute for the
  curator on multi-file planning-doc consistency.
- **evidence:** `planning/retros/_audit-phase-43.md` — 3 audit rounds,
  every FAIL a planning-doc gap, zero code defects.
- **classification:** workflow
- **status:** promoted
- **recurrence:** first occurrence (but note: the auditor has caught a
  planning-doc gap on *every* phase 41–43 — 41 plan Files, 42 obs, 43 ×3)
- **curation (Phase 43b follow-up triage, 2026-09-11, knowledge-curator):**
  dispatched specifically to close the gap the `release-phase-auditor`
  flagged (`planning/retros/_audit-phase-43b.md` observation 3): L-006 was
  committed to being triaged at Phase 43b's own triage but the first
  triage pass (which covered L-003/L-004/L-005) missed it. Verified two
  things independently, by reading the artifacts directly (no Bash
  available):
  1. **The amendment landed, textually, exactly as the `promoted_to` note
     describes.** `planning/agent-led-workflow.md` step 11 now reads:
     "If the retro schedules a follow-up phase, amends the roster or
     workflow, or otherwise changes the plan — re-dispatch
     `roadmap-context-curator` after writing it (step 10's reconciliation
     is now stale). Don't hand-patch the planning docs yourself; that
     drifts (GATE DA, Phase 43 — L-006)." `.claude/agents/roadmap-context-curator.md`
     "Hard rules" now opens with "Reconcile *every* planning doc, not just
     the top three," names `ROADMAP.md`/`CONTEXT.md`/`CHANGELOG.md` *and*
     `v1-redefinition/roadmap.md`, the phase's own `phase-N-*.md` status
     line, and any new `phase-*.md` a retro just scheduled, and
     cites "(GATE DA, Phase 43 — L-006)" as its own provenance. Both
     match the `promoted_to` note verbatim in substance.
  2. **The dispatching task's stronger claim — that the specific
     "re-dispatch after a plan-changing retro" clause fired and caught a
     premature `done` twice (43c and 43b) — does not hold up on a close
     read, and I'm not accepting it uncritically.** Re-reading both
     retros directly: `phase-43c-agent-context-pathways.md`'s own
     "Candidate learnings filed" section states outright "L-006 stays
     parked — its disposition confirmation is scheduled for Phase 43b
     triage… 43c's roster change was resolved *before* the
     `roadmap-context-curator` ran, so it did not re-trigger L-006's
     staleness pattern" — i.e., 43c is documented, in its own retro, as a
     case where the amendment's specific trigger condition (a
     *post*-curator-run plan change) never fired. Phase 43b's own retro
     "Where we're going" section doesn't schedule a new follow-up phase
     or amend the roster/workflow either — it just confirms "no gate
     blocks Phase 44." So neither phase is actually a case of the
     re-dispatch clause activating; the `release-phase-auditor`'s reports
     for both phases show the curator's step-10 run correctly holding
     `ROADMAP.md`/`v1-redefinition/roadmap.md`/the phase-plan status line
     at "in progress" pending retro+triage+audit — which is just the
     *ordinary* step-10 phase-end job (§5's "only if every DoD condition
     holds"), not the amendment's new re-dispatch mechanism specifically.
  3. **What the evidence *does* support, on the corrected reading: the
     amendment's broader remedy — multi-doc reconciliation instead of the
     lead hand-patching — has demonstrably worked, twice, on the exact
     failure shape L-006 recorded.** Phase 43 itself needed a 3-round
     `release-phase-auditor` trail (FAIL → FAIL → PASS), every FAIL a
     planning-doc bookkeeping gap across `ROADMAP.md` /
     `v1-redefinition/roadmap.md` / `CONTEXT.md`. Since the amendment
     landed, both Phase 43c (`_audit-phase-43c.md`) and Phase 43b
     (`_audit-phase-43b.md`) passed their `release-phase-auditor` audit on
     the **first round** (both "PASS WITH NON-BLOCKING OBSERVATIONS," no
     FAIL), with every named planning doc (`ROADMAP.md`,
     `v1-redefinition/roadmap.md`, the phase-plan status line,
     `CONTEXT.md`) found internally consistent (the only outstanding items
     in both were the expected pre-commit "still says in-progress, flip
     in the closeout commit" state and commit-hash placeholders — not
     bookkeeping contradictions). That is a real before/after: the
     specific defect pattern L-006 evidenced (planning-doc drift the lead
     alone couldn't keep straight) has not recurred across two
     subsequent phases. **Outcome: promote**, on this corrected basis —
     the amendment landed and the general remedy it encodes is working —
     while flagging that the narrower "re-dispatch after a plan-changing
     retro" trigger specifically remains untested (no retro since Phase
     43 has actually changed the plan *after* the curator's step-10 run)
     and should be watched the next time a GATE or retro does schedule a
     follow-up phase after step 10.
- **promoted_to:** `planning/agent-led-workflow.md` step 11 +
  `.claude/agents/roadmap-context-curator.md` "Hard rules" (re-dispatch
  after a plan-changing retro; reconcile every planning doc) @ `<commit>`
  — *lead fills the real short hash for the Phase 43 commit these landed
  in*.

### L-005 — `docs-maintainer` edited a generated file (it doesn't distinguish generated vs hand-authored)

- **origin:** Phase 43 (dogfood; `docs-maintainer` first *editing* use)
- **date:** 2026-09-10
- **project_revision:** 99c415c (+ Phase 43 commit)
- **observation:** `docs-maintainer` was asked to reconcile
  `.claude/skills/codecompass/SKILL.md` and edited it directly. That
  file is **git-tracked but generated** by
  `src/codecompass/skill.py::render_tool_skill` (written by `codecompass
  index`/bootstrap) — a direct edit is overwritten on the next `sync`,
  and the tracked file silently diverges from its generator meanwhile.
  The real fix belonged in `skill.py`. `docs-maintainer`'s brief lists
  the files it "may write" but says nothing about which are generated.
  (The agent *did* flag `.claude/commands/discovery.md` as generated and
  out of scope — so it has some awareness, just not applied
  consistently.)
- **evidence:** `.claude/skills/codecompass/SKILL.md` is in
  `git ls-files` (tracked) and not in `git check-ignore`; its content is
  produced by `render_tool_skill` (`tests/test_skill.py`); no test
  asserts the tracked file matches the generator, so drift is silent.
  The lead reverted the manual edit, fixed `skill.py`, and regenerated.
- **classification:** project-rule (the `docs-maintainer` brief rule —
  **promoted this phase**) + invariant (a `check_user_docs.py` rule that
  tracked generated artifacts match their generator output — tracked for
  Phase 43b as `check_generated_artifacts_match_source`)
- **status:** promoted
- **recurrence:** first occurrence
- **curation (Phase 43 GATE DA triage, 2026-09-10, knowledge-curator):**
  provenance accepted; evidence verified independently —
  `.claude/skills/codecompass/SKILL.md` exists at a checked-in path, its
  frontmatter `description` reads "generated by codecompass", and its
  body is produced by `src/codecompass/skill.py::render_tool_skill`
  (written to disk at `skill.py:129`,
  `(skill_dir / "SKILL.md").write_text(render_tool_skill(configs, project_root), …)`);
  `tests/test_skill.py` exercises `render_tool_skill` but no test asserts
  the tracked file equals the generator output, so drift is silent — the
  claim stands (the Phase 43 retro + `phase-43a` Files section assert the
  file is git-tracked; `git ls-files` not runnable here). **Split per
  GATE DA:**
  1. *project-rule part* — **promoted this phase.**
     `.claude/agents/docs-maintainer.md` "Hard rules" gained
     "**Before editing any file, check whether it is *generated*.**",
     naming `.claude/skills/codecompass/SKILL.md` explicitly and routing
     the fix to the generator (`src/…`, the lead's job). Logged in
     `promoted.md`.
  2. *invariant part* — a `check_generated_artifacts_match_source` rule
     in `check_user_docs.py` is now concrete scope in
     `planning/phase-43b-standing-doc-drift-checks.md` §2 (not a vague
     option). Not `promoted` until Phase 43b lands it + its test.
- **promoted_to:** `.claude/agents/docs-maintainer.md` "Hard rules"
  (generated-file check) @ d34a486 — *lead fills the real short
  hash*. Invariant part: pending Phase 43b.
- **curation (Phase 43b triage, 2026-09-11, knowledge-curator):**
  **invariant half now also promoted.** Verified independently:
  `check_generated_artifacts_match_source` is live in
  `scripts/check_user_docs.py` (L701-764, CHECKS list L781), comparing
  `.claude/skills/codecompass/SKILL.md` against
  `skill.render_tool_skill(...)` and `.claude/commands/discovery.md`
  against `commands.render_discovery_command()` — exactly the two
  artifacts named in `planning/phase-43b-standing-doc-drift-checks.md`
  §2, with the root `CLAUDE.md` routing table and per-vendor
  `codecompass-*` Skills explicitly noted as out of scope (not
  bare-function-reconstructable) rather than silently dropped. 4
  regression tests in
  `tests/test_check_user_docs.py::TestGeneratedArtifactsMatchSource`
  (L429-462), including `test_clean_against_real_repo` (L458) — this
  repo's own tracked `SKILL.md`/`discovery.md` verified to currently
  match their generators, closing the exact silent-drift failure mode
  this candidate recorded (`docs-maintainer` hand-editing
  `SKILL.md` in Phase 43). Both halves of L-005 (project-rule +
  invariant) are now closed; status updated to `promoted` in full.

### L-004 — the per-phase docs-drift audit is diff-scoped, so standing rot is invisible to it

- **origin:** Phase 42 (documentation lifecycle; `docs-maintainer` first real use)
- **date:** 2026-09-10
- **project_revision:** cd433f9 (+ Phase 42 commit)
- **observation:** the per-phase `docs-reconstructor` drift audit
  (`decisions/0050`) checks whether *this phase's diff* made a
  current-truth doc false. It cannot catch a doc that was **already**
  false before the phase and that no diff touches. `docs-maintainer`,
  reconciling Phase 42, found **4 passages in `architecture/overview.md`
  (Section C of `architecture-split-candidates.md`)** that describe
  deleted code (`grounded_description.py`, `_RAW_TEXT_CHAR_CAP`, the
  `Depth`/`depth = full` field) as live — errors that have survived
  every phase since Phase 16 (~25 phases) because no phase's diff went
  near those sentences. Same shape as L-003 (planning/** prose) — a
  diff-scoped check has a standing-rot blind spot.
- **evidence:** `planning/v1-redefinition/architecture-split-candidates.md`
  §C items 33–36; `architecture/overview.md` Known Footguns section vs.
  the same file's `## Grounded description — retired` / `## Cost model`
  sections (self-contradictory).
- **classification:** future-improvement
- **status:** promoted
- **recurrence:** first occurrence of this specific instance; second
  instance of the *pattern* shared with L-003 (see cluster note below).
- **curation (Phase 42 triage, 2026-09-10, knowledge-curator):**
  provenance accepted — evidence verified independently:
  `src/codecompass/grounded_description.py` does not exist (no file);
  `architecture/overview.md` §"Grounded description — retired" (L247) and
  §"Cost model" state `sync_vendor` makes no AI call ever, while the same
  file's Known Footguns (L1903–1913) still lists "Grounded description is
  fully regenerated … on every `sync` run" and `grounded_description.py`'s
  `_RAW_TEXT_CHAR_CAP` / `_DOCS_FILE_CAP` / `_ESTIMATED_COST_PER_CALL_USD`
  as live — self-contradictory; `Depth` / `VendorConfig.depth` are absent
  from `src/` entirely (`config.py` L41 shows `depth` is a legacy key
  that only parses), confirming split-candidates §C items 35–36 as
  false-as-live. `architecture-split-candidates.md` §C (items 33–36)
  exists and says what this candidate claims.
  **Outcome: retain**, split two ways:
  1. *The specific §C errors* are already escalated — catalogued in
     `planning/v1-redefinition/architecture-split-candidates.md` §C as
     Phase 61 input and recorded in `CONTEXT.md` "Still outstanding"
     (Phase 42). Recommendation handed to `roadmap-context-curator`: also
     pin "Phase 61 must fix architecture-split-candidates.md §C items
     33–36 as corrections, verified against `src/`" into the durable
     Phase 61 stanza of `planning/v1-redefinition/roadmap.md`, since
     CONTEXT.md's outstanding section is overwritten each session. Not
     the curator's file to write.
  2. *The general blind spot* (diff-scoped drift audit misses standing
     content) is the same insight as L-003 — see cluster note. The
     process choice (a `check_user_docs.py` "deleted-names must not
     appear as live" grep-rule / a between-milestones full-doc read /
     accept-and-wait-for-Phase-66) is a **GATE DA (Phase 43)** decision.
- **cluster:** L-003 + L-004 = the "standing-rot blind-spot" pair. Same
  shape (a diff-/product-scoped check has no eyes on content no diff
  touches); different scope (L-003 `planning/**` prose, no owner; L-004
  `architecture/**`, owned by `docs-maintainer`) and different fix, so
  **kept separate, not merged**. Both feed one GATE DA decision.
- **curation (Phase 43 GATE DA triage, 2026-09-10, knowledge-curator):**
  GATE DA ruled on the L-003 + L-004 cluster. Rather than broadening the
  `docs-reconstructor` drift-audit scope, it scheduled **Phase 43b** — a
  concrete, planned phase (`planning/phase-43b-standing-doc-drift-checks.md`,
  runs before Phase 44) — to add a **`check_no_deleted_names_as_live`**
  rule to `check_user_docs.py`: a hand-maintained list of retired names
  (`grounded_description`, `_RAW_TEXT_CHAR_CAP`, `Depth.FULL`,
  `depth = full`, `codecompass promote`, …) that must not appear as live
  in `README.md` / `docs/` / `architecture/` / `ai-docs/`. That is the
  standing-content complement to the diff-scoped audit and directly
  covers this candidate's `architecture/**` domain. Stays **retained →
  promoted-pending**: promote (with a `promoted.md` line) only once
  Phase 43b actually lands the check. The §C-specific fix remains a
  Phase 61 obligation (or gets pulled into 43b if clean — see the 43b
  plan's judgment call).
- **moves forward when:** Phase 43b implements `check_no_deleted_names_as_live`
  (now a concrete scheduled phase, not a vague GATE DA option) — then log
  the check + its regression test here and in `promoted.md`. Independently,
  Phase 61 landing the §C corrections also moves it forward (log that
  commit too). If Phase 43b slips past the Phase 47 bulk review, force
  promote/discard.
- **curation (Phase 43b triage, 2026-09-11, knowledge-curator):**
  **promoted — both halves closed.** Verified independently:
  (1) `check_no_deleted_names_as_live` is live in
  `scripts/check_user_docs.py` (CHECKS list, L780) and scoped to exactly
  L-004's own domain, `architecture/**` (via `_iter_doc_files`'s `docs`,
  `ai-docs`, `architecture`, `examples` dirs + `README.md`/
  `CONTRIBUTING.md`) — this is squarely inside L-004's original evidence
  location (`architecture/overview.md`), not by analogy the way L-003's
  case is. 5 regression tests in
  `tests/test_check_user_docs.py::TestNoDeletedNamesAsLive` (L387-426),
  including `test_clean_against_real_repo` (L425) and a
  false-positive-shaped `test_does_not_flag_historically_framed_mention`
  (L397) — directly answering this candidate's own evidence shape (a doc
  that "narrates decision history" and must not be flagged for doing so
  correctly). (2) L-004's originally-cited evidence — the 4
  self-contradictory `architecture/overview.md` passages (items 33-36)
  — is fixed, per
  `planning/v1-redefinition/architecture-split-candidates.md` L17-20 and
  L367-369 ("the 4 corrections were resolved in Phase 43b, leaving 32
  still outstanding for Phase 61"), independently re-verified by
  `docs-reconstructor`'s drift audit (`planning/retros/_drift-audit-phase-43b.md`,
  reported NO DRIFT — could not re-run myself, no Bash; trusting the
  retro's and the plan file's own reported result).
- **promoted_to:** `scripts/check_user_docs.py::check_no_deleted_names_as_live`
  + `tests/test_check_user_docs.py::TestNoDeletedNamesAsLive` (the
  general-mechanism half) + `architecture/overview.md` §"Known Footguns"
  / `architecture-split-candidates.md` §C items 33-36 (the
  motivating-evidence half) @ `<commit>` — *lead fills the real short
  hash for the Phase 43b commit*.

### L-003 — no independent check on `planning/**` narrative-doc accuracy

- **origin:** Phase 41 (first agent-led loop; `knowledge-curator` observation)
- **date:** 2026-09-10
- **project_revision:** c22d8e4 (+ Phase 41 commit)
- **observation:** `docs-maintainer` owns only `docs/`/`architecture/`/
  `README.md`/`ai-docs/`/`CONTRIBUTING.md`; the per-phase drift audit is
  scoped to *product* docs. `planning/**` prose (large and growing —
  `v1-redefinition/`, phase plans, workflow docs) has no independent
  accuracy check. `knowledge-curator` incidentally caught
  `planning/learnings/README.md`'s stale "not yet operational" status
  this phase; nothing systematic would have.
- **evidence:** the stale line
  (`planning/learnings/README.md` pre-Phase-41 "Status" section) was
  found only because the curator read broadly, not by any check or
  agent remit.
- **classification:** uncertain
- **status:** discarded (Phase 69 milestone bulk review, 2026-09-24 —
  see final curation note below)
- **recurrence:** pattern recurred — see the Phase 42 curation note below
  (L-004 is a second instance of the same diff-scoped blind-spot shape,
  in `architecture/**` rather than `planning/**`).
- **curation (Phase 41 follow-up triage, 2026-09-10):** confirmed
  **retain**. Real gap, not yet actionable — the resolution is a GATE DA
  process decision (Phase 43), not a promotable artifact today. Not
  merged with L-002: different subject (tool permissions vs. doc-accuracy
  ownership) and different owners.
- **curation (Phase 42 triage, 2026-09-10):** confirmed **retain**,
  unchanged. Pattern recurrence noted: **L-004** (Phase 42) is a second
  instance of the same shape — a diff-scoped check blind to standing
  content no diff touches — but in `architecture/**` (a current-truth
  product doc that *does* have an owner and a scheduled Phase 61 fix),
  not `planning/**` prose. Kept **separate, not merged**: different
  scope, owner, and fix. Treat L-003 + L-004 as one "standing-rot
  blind-spot" cluster for the GATE DA decision — together they are the
  evidence that the diff-scoped drift audit needs a standing-content
  complement.
- **curation (Phase 43 GATE DA triage, 2026-09-10, knowledge-curator):**
  GATE DA did not assign `planning/**` prose an owner or extend the
  drift-audit scope; instead it treated the L-003 + L-004 cluster as
  promotable via **Phase 43b**'s `check_no_deleted_names_as_live` rule
  (`planning/phase-43b-standing-doc-drift-checks.md` §2). Note the scope
  gap: that check as planned targets `README.md` / `docs/` /
  `architecture/` / `ai-docs/`, not `planning/**` prose — so it resolves
  L-004's domain squarely and L-003's only by analogy. Stays **retained
  → promoted-pending**. If a second stale-prose item is caught in
  `planning/**` specifically, that recurrence reopens the
  prose-ownership question separately.
- **moves forward when:** Phase 43b implements `check_no_deleted_names_as_live`
  (now a concrete scheduled phase, not a vague GATE DA option) — log it
  here and in `promoted.md` when it lands, **or** a second stale-prose
  item in `planning/**` is caught incidentally (recurrence → reopen
  prose-ownership). If still unresolved at the Phase 47 bulk review,
  force a promote/discard.
- **curation (Phase 43b triage, 2026-09-11, knowledge-curator):**
  `check_no_deleted_names_as_live` landed — verified directly in
  `scripts/check_user_docs.py::_iter_doc_files` (L333-342): it walks
  `README.md`, `CONTRIBUTING.md`, and `docs/` / `ai-docs/` /
  `architecture/` / `examples/`. **`planning/**` is not in that list.**
  L-003's own evidence (the stale `planning/learnings/README.md` "not yet
  operational" line, Phase 41) was a `planning/**` doc — squarely outside
  this check's scope. Confirms the Phase 43 GATE DA note's own caveat: the
  check "resolves L-004's domain squarely and L-003's only by analogy."
  It does not by analogy either, on inspection — `_RETIRED_NAMES` /
  `_HISTORICAL_MARKERS` matching logic is domain-agnostic, but the
  *file-selection* (`_iter_doc_files`) is the actual scope boundary, and
  it structurally excludes `planning/**`. **Outcome: split, not a clean
  promote.**
  1. The *general pattern half* shared with L-004 (a diff-scoped drift
     check has a standing-content blind spot; GATE DA's remedy shape —
     "a `check_user_docs.py` deleted-names-as-live rule" — is now proven
     workable) is real and now has landed evidence in the `architecture/**`
     instance. Credit that shared insight to **L-004's promotion** (below)
     rather than double-counting here.
  2. L-003's own specific claim — "no independent check on `planning/**`
     narrative-doc accuracy" — **remains true and unresolved.** No
     `planning/**` file is in `_iter_doc_files`'s scope, so nothing
     mechanical watches for a repeat of the exact incident L-003 records.
     **Status stays `retained`**, no longer "promoted-pending Phase 43b"
     (that pending resolution didn't materialize as hoped) — the gap is
     open-ended: extending `_iter_doc_files` to `planning/**` was never in
     scope for any phase and would need its own design (planning docs are
     allowed to describe *retired* things narratively far more than
     product docs are, e.g. superseded ADRs' summaries in roadmap prose —
     a blunt deleted-names-as-live rule over `planning/**` risks far more
     false positives than the product-doc version's own first draft did).
     Not proposing that extension without a second concrete incident to
     calibrate against, per L-003's own "moves forward when" clause.
  3. **Recurrence check:** no second `planning/**` stale-prose incident
     has been caught since Phase 41. The clause "a second stale-prose item
     in `planning/**` is caught incidentally" has not fired.
  4. **Phase 47 bulk-review flag:** L-003 has now been retained across
     Phases 41, 42, and 43b (3 phases) without promotion or discard —
     approaching but not yet past the ~3-phase staleness threshold this
     agent's brief asks it to flag. Note for Phase 47: if still
     unresolved then, force a promote (a scoped `planning/**`
     drift-check design) or discard (accept the gap as a known, bounded
     residual risk given `planning/**` isn't current-truth in the same
     sense product docs are).
- **promoted_to:** — (discarded at Phase 69's own milestone bulk
  review; see final curation note below)
- **curation (Phase 69 milestone bulk review, 2026-09-24, lead):**
  L-003's own "moves forward when" clause explicitly required a forced
  promote/discard at "the Phase 47 bulk review" if still unresolved by
  then — that forcing point was missed (Phase 47 was pure Ledgerkit-
  findings synthesis, no learnings-queue bulk disposition ran), and the
  entry sat `retained` for a further 21 phases without anyone actually
  making the call the entry's own text demanded. Found and forced now,
  at the actual milestone-closeout bulk retro review
  (`planning/phase-69-milestone-closeout.md` §1.2), rather than let it
  cross into v1 undispositioned. **Outcome: discard.** Reasoning: no
  second `planning/**` stale-prose incident has recurred in the ~68
  phases since Phase 41 (the entry's own recurrence clause never
  fired) — but this is not "the risk never materialized," it's that
  the *actual* mitigation that emerged is different in shape from what
  L-003 originally proposed (a per-file mechanical check) while still
  covering the same risk: this project's own planning docs have been
  through repeated, full, judgment-based bulk audits at nearly every
  major transition since — `roadmap-context-curator` dispatches at
  every phase boundary, the Phase 66 `CONTEXT.md` rewrite (which found
  and fixed a genuinely stale multi-thousand-line planning narrative),
  the Phase 66 `ROADMAP.md` full-table audit (three real findings),
  and Phase 68's own milestone-level audit (confirmed every phase's
  own retro/audit record) — none of which is the mechanical check
  L-003 asked for, but together they are a real, repeatedly-exercised,
  and repeatedly-successful check on exactly the class of drift L-003
  worried about. Building the originally-proposed blunt mechanical
  check now, at v1 milestone close, for a risk class the informal
  process has caught every real instance of for 68 phases, is not
  worth the false-positive risk the entry's own text already flagged
  (`planning/**` narrates retired concepts legitimately far more than
  product docs do). Not silently dropped — a conscious, reasoned
  milestone-time call, recorded in `planning/v1-closeout.md`'s own
  distilled process lessons.

### L-002 — `knowledge-curator` can't run the mechanical check it reasons about

- **origin:** Phase 41 (first agent-led loop)
- **date:** 2026-09-10
- **project_revision:** c22d8e4 (+ Phase 41 commit)
- **observation:** `knowledge-curator`'s `tools:` frontmatter is
  `Read, Grep, Glob, Edit, Write` (no Bash, by design). During the L-001
  triage it edited `planning/learnings/promoted.md` to resolve a
  `check_user_docs.py` finding but could not run the checker to confirm;
  it traced the check logic by hand and flagged it for the lead.
- **evidence:** the agent's own report ("I could not execute the checker
  (Bash is disabled in this session)").
- **classification:** workflow (a documented "lead runs the confirming
  check" handoff step) + scoped-rule (the `knowledge-curator` brief
  amendment)
- **status:** promoted
- **recurrence:** 2nd occurrence — Phase 42 triage (2026-09-10,
  `knowledge-curator`): while editing L-004's provenance in `inbox.md`,
  the curator again could not run `python scripts/check_user_docs.py`
  (Bash disabled for this session and its subagents) and traced the four
  learnings checks by hand instead. This is the "2nd occurrence" trigger
  named in "moves forward when" below — GATE DA (Phase 43) now has a
  concrete recurrence, not just the Phase 41 first instance.
- **curation (Phase 41 follow-up triage, 2026-09-10):** confirmed
  **retain**. Genuine, but the fix is a GATE DA choice between two
  designs (read-only Bash in the `knowledge-curator` `tools:` frontmatter
  vs. a documented "lead runs the confirming check" handoff step in
  `agent-led-workflow.md`) — neither is a promotable artifact until that
  choice is made. A `tools:` change would be a `.claude/` scoped-rule
  edit (lead finalises); the handoff would be a workflow-doc edit. Not
  merged with L-003 (unrelated subject).
- **curation (Phase 43 GATE DA triage, 2026-09-10, knowledge-curator):**
  **promoted.** GATE DA chose the "lead runs the confirming check"
  handoff over read-only Bash — `tools:` can't scope Bash to read-only,
  and the v0.2 file-deletion incident makes unrestricted Bash a real
  risk. Landed this phase:
  - `planning/agent-led-workflow.md` step 12 now requires the curator's
    final message to end with an explicit "lead: run `<command>` to
    confirm" line, and states the lead runs it before accepting the
    triage.
  - `.claude/agents/knowledge-curator.md` "Hard rules" gained the
    matching "**You have no Bash.** … end your report with an explicit
    'lead: run `<command>` to confirm' line" rule.
  This is now the 3rd occurrence (every Stage A triage — Phases 41, 42,
  43); the recurrence trigger below is satisfied. Logged in `promoted.md`.
- **moves forward when:** resolved — promoted this phase.
- **promoted_to:** `planning/agent-led-workflow.md` step 12 +
  `.claude/agents/knowledge-curator.md` "Hard rules" @ d34a486
  — *lead fills the real short hash*.

### L-001 — `check_readme_phase_count` conflated "highest done phase" with "product completeness"

- **origin:** Phase 40 (standing up the agent-led roster)
- **date:** 2026-09-09
- **project_revision:** 9ca97ed (observed); fixed in c22d8e4
- **observation:** `scripts/check_user_docs.py::check_readme_phase_count`
  required README's "phases 0-N" claim to equal `max(done phase in
  ROADMAP)`. The redefined-v1 Stage A–F phases (39+) are a
  process/validation milestone group, not product features — every one
  of them marked `done` would have forced a misleading README bump
  ("phases 0-43 done!" implies more shipped product than exists) or left
  the `--strict` DoD gate permanently red across Stage A.
- **evidence:** the check FAILs the moment Phase 40's ROADMAP row flips
  to `done` while README honestly says "phases 0-38" (the foundation).
  Fixed in this phase's commit by excluding ROADMAP content from the
  `## Redefined CodeCompass v1` heading onward; regression test
  `tests/test_check_user_docs.py::TestReadmePhaseCount::test_ignores_done_phases_in_redefined_v1_section`.
- **classification:** invariant (the fix + regression test landed with
  Phase 40; this entry records *why*)
- **status:** promoted
- **recurrence:** first occurrence
- **promoted_to:**
  `tests/test_check_user_docs.py::TestReadmePhaseCount::test_ignores_done_phases_in_redefined_v1_section`
  + `scripts/check_user_docs.py::check_readme_phase_count` @ c22d8e4
  (logged in `promoted.md`, Phase 41 triage 2026-09-10)
