# Phase 81B Amendment 4 (model-broker inference boundary, unblocking the credential gap) — independent completion audit

- **Auditor:** release-phase-auditor (independent subagent pass)
- **Date:** 2026-10-10
- **HEAD audited:** `027bd9a` (branch `main`, matches `origin/main` exactly —
  `git log origin/main --oneline -5` returns the identical commit list as
  local `HEAD`; working tree clean).
- **Commits in scope:** `d4ebd41` (amendment plan) through `027bd9a`
  (changelog rewrite), 26 commits total — one more than the ~25 named in
  the dispatch (the final changelog-rewrite commit `027bd9a` landed
  after dispatch and is included here since it is part of the exact
  state being audited).
- **Framing:** amendment 4 claims the phase is now fully delivered (not
  `blocked`). `planning/ROADMAP.md` still shows Phase 81B as `in progress
  (amendment 4)` — correctly not yet flipped to `done`, since that flip
  is the terminal `roadmap-context-curator` action this audit exists to
  authorize or block.

## Verdict: **FAIL**

One genuine, well-evidenced, blocking gap: `planning/CONTEXT.md` does
not reflect amendment 4's actual, shipped final state — it still
describes the phase as of the plan commit (`d4ebd41`), before any of the
26 commits of real implementation happened. **This is the identical
defect category independently flagged as a blocking FAIL for both Phase
79 and Phase 80** (`planning/retros/_audit-phase-80.md` §1, which itself
names the Phase 79 recurrence) — it has now recurred a third time, on
this project's single most consequential and highest-commit-count phase
to date. Every other condition checked below — the broker's isolation
properties, the cold-reader/writer run, the documentation disposition,
the template repository, the test suite, lint, doc-checks, protected
files, and the changelog — was independently re-verified and found
genuinely accurate. Two further non-blocking observations are also
recorded (an explicitly self-disclosed follow-up gap that fell out of
the learning triage, and a missing ADR for the amendment's own
architecture decision).

## 1. Blocking finding: `planning/CONTEXT.md` does not reflect the new state

`planning/CONTEXT.md` was last touched at `d4ebd41` (the plan commit
itself, "amendment 4 — model-broker inference boundary to unblock the
credential gap") and never touched again across the 25 subsequent
commits that actually built the broker, ran 11 cold-reader passes,
produced and preserved the writer's output, executed the legacy-gap
review, executed documentation disposition against both `codecompass`
and `codecompass-template`, published the durable workflow document, and
closed out tests/lint/learnings/retro.

At the audited `HEAD` (`027bd9a`), `planning/CONTEXT.md` still reads,
verbatim:

- **"Current phase"** (lines 8-56): "Phase 81B is reopened, in progress,
  under a fourth amendment... attempting to remove the specific
  credential-provisioning blocker." It then describes only the
  *investigation* (broker finding 1-5) and states **"Per the plan's own
  Amendment 1 hard gate, the authoritative writer run, cold-reader,
  result branches, and documentation disposition execution correctly
  did not proceed."** This sentence is false as of `HEAD` — all four of
  those things did proceed, succeeded, and are the bulk of what this
  amendment delivered.
- **"Next concrete step"** (lines 122-139): lists, as still-pending
  work, "build and test `scripts/cleanroom_broker.py` and its
  isolation/canary test suite; revalidate the existing
  `documented_revision`/`handoff_commit`... run the cold-reader inside
  verified Mode B + broker; run the authoritative writer and preserve
  its output...; perform the legacy gap review; perform documentation
  disposition for both repositories; persist the durable workflow
  document; run the full closeout sequence (defect re-review,
  tests/lint, docs-drift audit, learning triage, retro, independent
  completion audit)." **Every one of these is independently confirmed
  complete** (see §§2-7 below) — none of them is actually a next step.

This is a direct violation of `CLAUDE.md` §5's DoD condition
("`planning/CONTEXT.md` reflects the new state") and §4 ("overwrite the
current-state section each time"). It is not covered by §5's narrow
terminal-reconciliation exemption — per that exemption's own text and
per the Phase 80 precedent's own reasoning, the exemption covers only the
*final* flip of `CONTEXT.md`'s current-state section to describe the
phase as `done`, performed by the lead/`roadmap-context-curator` *after*
a passing audit. It does not excuse leaving `CONTEXT.md` describing a
phase as blocked/not-yet-started through 25 real, shipped, commits'
worth of work, with next-step prose that is now simply false.

**What must be fixed before re-audit:** rewrite `planning/CONTEXT.md`'s
"Current phase" and "Next concrete step" sections (and "What was just
completed" if it also predates `d4ebd41`'s descendants) to accurately
describe: the broker built and isolation-verified (including the
launch-directory-leak fix); 11 cold-reader passes to `SUFFICIENT`; the
authoritative writer run and its preserved output; the legacy-gap
review (5 real gaps reconciled); documentation disposition executed
against both repositories (77 files in `codecompass`, 9 in
`codecompass-template`, both pushed); the durable workflow document
published at `docs/development/clean-room-redocumentation.md`; and the
closeout sequence (tests/lint/docs-audit/learning-triage/retro) as
complete — while still correctly stating the phase is pending its own
DoD gate (not yet flipped `done` on `ROADMAP.md`), exactly as Phase 80's
own fix (and this audit) requires.

## 2. Broker isolation — independently re-verified, genuinely holds

Read `scripts/cleanroom_broker.py`, `scripts/cleanroom_broker_client.py`
directly.

- `_sanitize_env()` returns a **fixed literal dict** (`{"PATH": ...,
  "HOME": ...}`), built with no reference to `os.environ` at all — a
  genuine allow-list, not a deny-list with a gap. Confirmed by direct
  read, not by trusting the docstring.
- Response schema `_RESPONSE_FIELDS = {"ok", "output", "usage",
  "error"}`; request schema `_REQUEST_FIELDS = {"system_prompt",
  "messages", "max_turns"}` — no field for a file path, shell command,
  URL, or tool/MCP config exists in either direction, confirmed by
  direct read of `handle_request`/`run_inference`.
- `cleanroom_broker_client.py` (the only thing bind-mounted into the
  sandbox) is 51 lines: opens exactly one Unix socket, sends one JSON
  line, reads one JSON line. No filesystem, shell, or network primitive
  anywhere in the file.
- Ran `python -m pytest tests/test_cleanroom_broker.py
  tests/test_cleanroom_prompt_assembler.py -v`: **32 passed** (27 in the
  broker file — 25 unit + 2 live — plus 5 in the prompt-assembler file),
  matching the claimed "~25 unit + 2 live" count exactly. All genuinely
  exercise the claimed properties (credential redaction, env
  allow-listing, fresh-session-id-per-call, fail-closed on
  auth/parse/timeout failure, the neutral-cwd regression test).
- `planning/phase-81b-broker-isolation-investigation.md`'s real sandbox
  test transcript (socket-only reachability, PID-escape attempt,
  `/proc/mounts` dump, the canary test) is internally consistent with
  the broker code read directly above — no claim in that report
  contradicts the actual implementation.

## 3. Clean-room branches — independently re-verified, genuinely valid

- `git ls-remote origin refs/heads/cleanroom/redoc-b939d23
  refs/heads/cleanroom/result-8325272` — both exist on `origin`, exactly
  as claimed.
- Extracted a fresh `git archive` of `cleanroom/redoc-b939d23` into a
  clean scratch directory and ran `python -I
  scripts/prepare_cleanroom_branch.py validate <dir>` against it:
  **`PASS: staging tree matches its own manifest exactly`** — this
  validator independently checks excluded-path absence, manifest
  completeness in both directions, and a fresh SHA-256 re-hash of every
  `intermediary_projection_hashes` entry against the real current
  `planning/knowledge/` content, not merely "a manifest file is present."

## 4. Documentation disposition — independently re-verified, matches the plan's own disposition table

- `git show --stat 7cb09c5`: spot-checked 9 specific
  deletions/replacements named in the plan's own disposition table
  (`docs/quickstart.md`, `docs/cli-reference.md`, `docs/config-schema.md`,
  `docs/codecompass-knowledge-workflow.md`, `docs/external-adapters.md`,
  `docs/developer/`, `architecture/overview.md`,
  `architecture/historical-notes.md`, `docs/domain/`) — all genuinely
  absent from the working tree now; the new `docs/` tree has exactly 24
  files across the 6 directories the plan named.
- `architecture/historical-notes.md`'s two real stories are genuinely
  incorporated, not dropped: `docs/architecture/data-and-control-flow.md`
  line 47 ("Historical note: why generated-artifact refresh runs where
  it does") and `docs/workflows/sync-and-enrichment-pipeline.md` line 34
  (the fixed-window-vs-chunk-centering historical note) both contain
  real, substantive incorporated content, not placeholder pointers.
- `CONTRIBUTING.md` — confirmed its own CLAUDE.md-mirroring governance
  sections ("Plan before implementing," "Definition of done, per phase,"
  the agent-led-development description) are intact, unmodified in
  substance. The disposition commit's own claim "correctly left
  UNTOUCHED" is **slightly imprecise** (the file *was* touched, by the
  same commit, for two dead-link path fixes — `docs/codecompass-
  knowledge-workflow.md` → `docs/workflows/knowledge-reconciliation-loop.md`
  and a `README.md` Setup→Installation section-name fix) but the
  substance of the claim (governance content preserved, not overwritten
  with clean-room-writer content) is accurate. Non-blocking.
- `docs/development/clean-room-redocumentation.md` exists (the durable
  workflow document), published only after the run succeeded, as the
  plan required.

## 5. `codecompass-template` disposition — independently re-verified in the sibling repository

- In `/home/cormac/projects/codecompass-template`: `dff3f4d` exists,
  local `HEAD` and `origin/main` are identical (`git log --oneline -5`
  matches on both).
- `optional-intermediate-knowledge/README.md` genuinely contains the
  honest disclosure claimed by the retro: *"no template files for this
  directory were available in the evidence used to write this
  documentation... Don't treat this page as a spec; treat it as a
  placeholder description until real templates exist here to document
  properly."* This is real, substantive honest disclosure, not
  fabricated template content.

## 6. Defect-class regression sweep — spot-checked directly, holds for the 3 checked; the sweep itself has no persisted dedicated artifact

Spot-checked 3 of the 12 named defect classes directly against current
code (not the retro's own narrative):

- **Deny-list isolation** → confirmed genuine allow-list (§2 above).
- **Raw filesystem walks (branch-manifest mismatch root cause)** →
  `scripts/prepare_cleanroom_branch.py`'s only filesystem-walk call
  (`staging.rglob("*")`) is inside `cmd_validate`, used only to confirm
  nothing *unlisted* leaked into an already-built staging tree — file
  **inclusion** itself is still derived from `git ls-files`
  (`_git_tracked_files`), not a raw walk, confirmed by direct read and
  by `tests/test_prepare_cleanroom_branch.py`'s 11 passing tests
  (including the L-097 submodule-toplevel regression test).
- **Destructive worktree handling** → `cmd_build` explicitly checks for
  a `.git` link file (a worktree marker) before any `rmtree` and fails
  closed rather than destroying it (lines 250-260).

All three genuinely hold. However, unlike every other major step of this
amendment (which each got a dedicated, committed artifact — the broker
investigation, the cold-reader verdict, the legacy-gap review, the
template redocumentation note), **no dedicated artifact exists recording
the claimed 12-defect-class first-principles sweep itself** — it is
referenced only in the retro's prose ("a defect-class regression sweep
confirming none of the twelve named failure categories recurred
undetected") with no commit, report, or checklist naming the 12
categories and their individual dispositions. Non-blocking given my own
3-class spot-check held, but worth noting as a weaker evidence trail
than every other claim in this amendment.

## 7. Tests, lint, doc checks — all independently re-run, all genuinely pass

- `python -m pytest -q`: **899 passed, 2 skipped** — matches the
  disposition commit's own claimed count exactly.
- `ruff check .`: **All checks passed!**
- `python scripts/check_user_docs.py --strict`: **no findings**.
- `python scripts/check_knowledge_base.py --strict`: **24 findings, all
  `(info)`-level `knowledge-base-snapshot-current-divergence`** — matches
  the claimed "only pre-existing info-level snapshot-divergence
  findings, nothing else" exactly; no higher-severity finding present.

## 8. Protected files — confirmed clean

- `git diff d4ebd41..HEAD -- CLAUDE.md`: **empty**. `CLAUDE.md` was not
  touched anywhere in this amendment's range.
- No past ADR's original content was edited (checked `git diff
  d4ebd41..HEAD --stat -- decisions/`: **empty** — no ADR touched at
  all in this range, see §10 below).

## 9. Changelog — fixed during this amendment's own closeout, now correct

`CHANGELOG.md`'s Phase 81B entry originally (through commit `8154172`,
the state named in the dispatch) still described the pre-amendment-4
`BLOCKED` outcome — repeating the exact gap class an earlier audit of
this same phase's first implementation had to catch. This was caught and
fixed in the amendment's own final commit, `027bd9a` ("update the
changelog entry to reflect amendment 4's final, true outcome"), landed
*after* the dispatch prompt was written but *before* this audit ran
against `HEAD`. The rewritten entry is a single, consolidated `[Phase
81B]` entry (not a confusing second entry appended alongside the old
one) and accurately summarizes the broker, the 11 cold-reader passes, the
legacy-gap review, both repositories' disposition, and the workflow
document. Confirmed via `grep -n "Phase 81B" CHANGELOG.md`: exactly one
entry. This item is resolved, not a finding.

## 10. Non-blocking observation: a self-disclosed follow-up gap was flagged for learning triage but never actually triaged

Commit `7cb09c5`'s own message explicitly states: *"NOT yet addressed in
this commit... several `.claude/agents/*.md` files
(`docs-reconstructor.md`, `docs-maintainer.md`, `context-researcher.md`,
`domain-skeptic.md`, `release-phase-auditor.md`) contain conditional
logic keyed on 'once `docs/domain/` exists' / assume
`architecture/overview.md` as a stable example path — both now
permanently stale given `docs/domain/` is gone and
`architecture/overview.md` moved. This is a real, genuine follow-up gap,
flagged here explicitly for the closeout's own learning triage rather
than fixed now."*

Independently confirmed this gap is real and still present: `architecture/`
no longer exists at all (`ls architecture` → "No such file or
directory"), `docs/domain/` does not exist, and `grep` confirms
`docs-reconstructor.md`, `context-researcher.md`, `domain-skeptic.md`,
and `release-phase-auditor.md` (this auditor's own charter) all still
reference one or both paths as if current. The later commit that did
reconcile stale paths (`7716073`, "reconcile remaining stale doc-path
references in source docstrings/error strings") touched only
`src/codecompass/*.py` — none of the 5 `.claude/agents/*.md` files.

Checked the actual learning triage (`1a864df`, 6 candidates: L-092
through L-097) and `planning/context-gaps/inbox.md` (last touched
2026-10-02, before this amendment) — **this specific, self-disclosed gap
was not filed as any of L-092–L-097, nor as a context-gap, nor fixed
anywhere else in the range.** It was explicitly flagged for triage and
then fell out of the actual triage pass. This is a real, if narrow, gap
in DoD condition 5 ("candidate learnings from the phase — including any
surfaced by the retro — have been triaged"): one candidate the phase
itself raised was never triaged at all, rather than triaged and
discarded/retained with a reasoned note. Non-blocking relative to the
§1 finding, but should be filed (as a learning or a context-gap) before
or alongside the CONTEXT.md fix, not silently dropped a second time.

## 11. Non-blocking observation: no ADR for the amendment's own architecture decision

The amendment's central, non-obvious tradeoff — give the sandbox an
*inference capability* instead of a *credential*, accepting a named,
content-neutral residual (email/date/token-budget/OS-type/generic
security-policy reminder) as non-disqualifying, per a judgement call
explicitly put to the user (plan §26.1) — is exactly the kind of
decision `CLAUDE.md` §2 asks for a new ADR for ("whenever a phase
involves a non-obvious tradeoff, not only for decisions already known at
project start"). No ADR was written for it: `git diff d4ebd41..HEAD
--stat -- decisions/` is empty, and `decisions/0066` (the only existing
ADR mentioning clean-room isolation) predates this amendment entirely
(Phase 79) and does not mention the broker, the credential/capability
distinction, or the Finding-4 residual. The plan's own §26 never commits
to writing one either. This is a real documentation gap under §2, not a
re-litigation of whether the broker design itself was correct (which
this audit does not question).

## What must be fixed before re-audit

1. **Blocking:** rewrite `planning/CONTEXT.md`'s "Current phase," "What
   was just completed," and "Next concrete step" sections to accurately
   describe amendment 4 as fully delivered through the closeout sequence
   (broker, 11 cold-reader passes, writer run, legacy-gap review, both
   repositories' disposition, workflow document, tests/lint/retro/
   learning-triage) — while still correctly stating the phase is
   pending its own DoD gate (not yet `done` on `ROADMAP.md`).
2. **Non-blocking, should accompany the above:** file the
   `.claude/agents/*.md` stale-`docs/domain/`/`architecture/overview.md`
   -reference gap (self-disclosed in `7cb09c5`) as a learning or
   context-gap — it was flagged for triage and then dropped.
3. **Non-blocking:** consider a new ADR for the model-inference-broker
   (capability-not-credential) design decision, per `CLAUDE.md` §2.

Once (1) is fixed, re-audit; items (2)-(3) do not themselves require a
further audit cycle if the lead judges them acceptable to track via the
normal learning/ADR backlog rather than blocking this phase's `done`
flip, but should not be silently left unaddressed either.
