# Learnings inbox

The live queue. New candidates go at the top. Format: `TEMPLATE.md`.
Curation rules: `planning/v1-redefinition/learning-lifecycle.md`.

Statuses: `candidate` → `evidence-gathering` → `promoted` / `retained` /
`merged:<id>` / `discarded`.

---

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
- **status:** candidate
- **recurrence:**
- **promoted_to:**


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
  (unscheduled)" section
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
  (unscheduled)" section
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

### L-023 — a newly-created `.claude/agents/*.md` file is not immediately dispatchable by its own type name

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
- **recurrence:** first occurrence
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
- **status:** candidate
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
- **status:** retained
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
- **promoted_to:** — (retained; `planning/**` scope gap still open,
  unrelated to Phase 43b's landed check; flagged for Phase 47 bulk review)

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
