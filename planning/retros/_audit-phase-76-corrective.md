# Phase 76 corrective-pass completion audit — `release-phase-auditor`

**Scope:** independent Definition-of-Done audit of Phase 76's
post-closeout corrective pass — the nine-commit sequence `feaaaa0` ..
`8ab36aa` on `main`, applied on top of the original closeout at `b3abe07`
(already audited once, `planning/retros/_audit-phase-76.md`, PASS WITH
NON-BLOCKING OBSERVATIONS). This is **not** a re-litigation of Phase 76's
original scope — only of the corrective pass itself, per `CLAUDE.md` §5's
requirement that any commit landing after an audit and touching audited
scope voids it and requires a fresh pass. Audited commit: `8ab36aa`
(current `HEAD` at audit time).

**Verdict: PASS WITH NON-BLOCKING OBSERVATIONS — with one item that
blocks the final `done`-flip specifically** (see Finding 1; not a defect
in the corrective work itself, but a precondition the terminal
reconciliation must not proceed without).

## What was re-run (all independently, against the actual working tree)

1. `.venv/bin/pytest -q` → **694 passed, 2 skipped** (199.51s). Matches
   the expected "~694+ passed given 6 new tests" (4 in `test_cli.py`, 2
   in `test_git_topology.py`).
2. `.venv/bin/ruff check .` → **All checks passed!**
3. `python3 scripts/check_user_docs.py --strict` → **no findings**.
4. `python3 scripts/check_knowledge_base.py` → **no findings**.
5. `.venv/bin/pytest -q tests/test_git_topology.py -v` → **32 passed**
   (isolated re-run, confirms the pre-existing bare-repo/not-a-
   repo/generic-failure classification tests still pass alongside the
   two new version-floor tests).
6. `.venv/bin/pytest -q tests/test_cli.py tests/test_git_topology.py` —
   also independently re-run as part of spot-checking the drift audit's
   own claim (117 passed, matching the drift audit's own count).
7. Live CLI run against a disposable scratch Git repository (built and
   destroyed under the session scratchpad, not under the project):
   `git init`, one commit, one uncommitted edit, `vendor.toml` stub,
   `codecompass sync`, `codecompass query topology` → rendered
   `workspace: dirty` correctly for a genuinely dirty real worktree.
   Scratch directory removed after use; confirmed via `git status`/
   `git worktree list` that no scratch artifact, stray worktree, or
   uncommitted project file resulted from this step.

## Item-by-item findings

### 1. CLI rendering fix (`_tri_state_label`/`_render_topology`) — REAL, COMPLETE

Read `src/codecompass/cli.py` directly and diffed `b3abe07..db33352`.
`_tri_state_label(value, when_true, when_false, when_none)` (lines
951-962) is a genuine three-way dispatch (`is True` / `is False` / else)
— never Python truthiness. All three previously-buggy call sites are
fixed:
- line 1000: current-worktree `is_dirty` → `dirty`/`clean`/`unknown`.
- line 1022-1027: submodule `revision_matches_pin` → `matches pin`/
  `differs from pin`/`comparison unresolved`.
- line 1031: submodule `child_is_dirty` → `dirty`/`clean`/`unknown`.

`--json` path (lines 970-974) is untouched: `json.dumps({"indexed": True,
**profile}, ...)` — raw nullable pass-through, confirmed via the new
`test_query_topology_json_preserves_nullable_values_unchanged` test
(asserts `is_dirty`/`revision_matches_pin`/`child_is_dirty` are `None` in
the JSON payload) and by direct code read. Four new regression tests in
`tests/test_cli.py` each construct the specific `None` fixture state and
assert the honest label appears and the false-certainty label does not.
Live CLI run (non-`None` case) confirms real rendering still works for
the ordinary path.

### 2. Git minimum-version fix (`_detect_git_version`/`_MIN_GIT_VERSION`) — REAL, COMPLETE, CORRECTLY SEQUENCED

Read `src/codecompass/git_topology.py` directly. `_MIN_GIT_VERSION = (2,
7)` (line 71); `_detect_git_version` (lines 223-239) parses `git
--version` via `_GIT_VERSION_RE`, returns `None` (never blocks) on any
failure/unparseable output, and only a version that parses **and** is
`< _MIN_GIT_VERSION` short-circuits. The call site (line 300, inside
`detect_git_topology`) runs **after** the initial `rev-parse
--show-toplevel --git-common-dir` call has already succeeded and been
classified (not-a-repo and bare-repo branches both already returned by
this point) and **before** `_detect_origin_url` (`git remote get-url`,
line 312) and `_detect_worktrees`/`_detect_submodules` (`git worktree
list`, called inside those) — exactly the required sequencing. A
version-floor violation returns `UNAVAILABLE` with an explicit,
version-naming reason and never reaches either 2.7-gated command
(confirmed by the new test's own assertion that neither `["worktree",
"list", ...]` nor `["remote", "get-url", ...]` is ever called in that
path).

Pre-existing classification paths (`not_git`, bare-repository
`UNAVAILABLE`, generic-rev-parse-failure `UNAVAILABLE`) are unmodified
and still covered — `tests/test_git_topology.py` re-run in isolation:
32/32 passed, including `test_bare_repository_is_unavailable_not_a_crash`
unchanged. Two new tests (`test_git_older_than_2_7_is_unavailable_...`,
`test_git_version_unparseable_does_not_block_detection`) directly
exercise the new code, live against a real `git init`'d repo with only
`--version`'s own output monkeypatched — not a fully-mocked unit test.

`decisions/0063` diffed `b3abe07..HEAD` for this file: **empty** — the
original (now-superseded) Git-2.5 claim at point 8 is genuinely
untouched, matching the append-only convention. `decisions/0064` is a
real, substantive ADR (Status/Context/Decision/Alternatives/
Consequences all filled with specific, checkable evidence — a local
`Documentation/RelNotes/2.7.0.txt` citation and specific `git/git`
tag/file references), following the exact append-only-supersession shape
`decisions/0061` established for the same kind of gap (superseding a
past ADR's claim without editing it).

Doc updates confirmed present and correct in all five named files —
`architecture/overview.md:788-796`, `architecture/context-graph-
schema.md:163-169`, `docs/cli-reference.md:232-236`, `README.md:157`,
`ai-docs/README.md:49` — each states "Requires Git 2.7+" with the
`--git-common-dir`-is-2.5-but-two-other-calls-need-2.7 nuance, matching
the module docstring and the real `_MIN_GIT_VERSION`/reason-string code
exactly (spot-checked two of these directly by reading the file content
myself, not merely trusting the drift audit's own quotes).

### 3. `CLAUDE.md` §5 exemption — COHERENT, NARROWLY SCOPED, NO DRIFT ACROSS DOCS

Read `CLAUDE.md` §5's current text directly. The exemption clause names
exactly three targets (`planning/ROADMAP.md`'s phase row,
`planning/CONTEXT.md`'s current-state section, the phase plan file's own
Status line) and explicitly re-states that anything else voids the audit
— the general "any commit voids the audit" rule is unweakened for every
other file/case. Cross-checked against `planning/agent-led-workflow.md`
step 14 and `.claude/agents/roadmap-context-curator.md`'s "Terminal
done-flip reconciliation" section: both name the identical three targets
and the identical excluded-category list, verbatim in substance. No
drift among the three documents.

### 4. `L-065` triage — content is genuine and substantive, but **not committed**

`planning/learnings/inbox.md`'s `L-065` entry (working tree, current
state) has `status: promoted`, a `promoted_to` field naming the exact
landed artifacts and commits, and a real, multi-paragraph curation note
dated to this corrective pass — not a bare status flip. It independently
re-verifies the exemption's internal consistency, the three-document
cross-check, a scope-narrowness check, and even flags one genuinely
separate, non-blocking, out-of-scope wording looseness in
`release-phase-auditor.md` for future awareness. This is real curation
work, not a rubber stamp.

`planning/learnings/promoted.md` has a matching `L-065` pointer line.

**However:** `git diff --stat` at `HEAD` (`8ab36aa`) shows
`planning/learnings/inbox.md` and `planning/learnings/promoted.md` as
**modified, uncommitted** working-tree changes — this triage exists only
in the working directory, not in any commit through `8ab36aa`. The
corrective-pass commit sequence audited here (`feaaaa0`..`8ab36aa`) does
**not** include this triage; `6d668db` filed `L-065` as `candidate` only.
This is a real gap: per this audit's own charter ("against the exact
commit about to be marked `done`"), an uncommitted change is not durable
evidence and is not part of the state this or any future audit can
verify from git history alone. **This must be committed as its own
commit (matching this project's established practice of a dedicated
learnings-triage commit) before the terminal `roadmap-context-curator`
reconciliation runs** — and, per the newly-fixed §5 exemption itself,
that triage commit is emphatically *not* one of the three exempt
targets, so it must land strictly *before* the terminal reconciliation
commit, not folded into or after it.

### 5. Retro corrective-pass addendum — SUBSTANTIVE

`planning/retros/phase-76-git-repository-topology.md`'s "Corrective-pass
addendum" section (read in full) covers what was found (all three
defects, with real detail), how each was fixed, what worked, what didn't
work / process gaps surfaced (explicitly not over-expanded into new
rules, per the user's own narrow-scope instruction), the corrective-pass
commit list, and the closeout sequence still required. Not a stub.

### 6. Drift audit — GENUINE, INDEPENDENT, NO DRIFT — spot-checked

`planning/retros/_drift-audit-phase-76-corrective.md` read in full.
Independently spot-checked two of its own claims against real source
rather than trusting its text:
- `README.md:157` and `architecture/overview.md:788-796` — both read
  directly; wording matches the drift audit's quotes exactly.
- `docs/domain/` sweep claim (only "submodule" hits are the
  reference-project protocol submodule sense, unrelated to
  `git_topology.py`) — independently re-grepped
  `docs/domain/references.md`, `docs/domain/concepts/protocol.md`,
  `docs/domain/concepts/capability.md` myself; confirmed the same three
  hits, same unrelated sense. Also independently confirmed via
  `git diff --stat` that the corrective pass touched **zero** files under
  `docs/domain/` — so the full-page-read requirement (item 9's own
  Phase-74/`L-061` lesson) does not apply here; a grep-only check is
  legitimately sufficient for a pass that never touched any domain
  concept page.

The drift audit's own verdict (NO DRIFT) holds up under this independent
re-check.

### 7. ROADMAP.md / CONTEXT.md state — CORRECTLY "in progress", not "done"

Both `planning/ROADMAP.md`'s Phase 76 row and `planning/CONTEXT.md`'s
current-phase/what-was-just-completed sections consistently describe
Phase 76 as reopened/`in progress`, list the same three defects and the
same still-pending closeout steps (retro addendum, drift audit,
`L-065` triage, this audit, final reconciliation). This is expected at
this point in the sequence, not a finding.

### 8. Scope creep check — NONE FOUND

Full diffstat `feaaaa0~1..8ab36aa` (21 files) accounted for entirely by:
the two named source modules + their test files; the five named
current-truth docs; `decisions/0064` (new); `CLAUDE.md` (approved);
`.claude/agents/roadmap-context-curator.md` and
`planning/agent-led-workflow.md` (operationalization);
`CHANGELOG.md`/`planning/CONTEXT.md`/`planning/ROADMAP.md`/plan
file/retro (process docs); `planning/learnings/inbox.md` (the `L-065`
filing commit, `6d668db` — separate from the still-uncommitted triage,
Finding 1); `planning/v1-redefinition/proposed-governance-changes.md`
(§F backfill, matching the §D/§E precedent named in the task). Nothing
outside the three named defects and their direct, necessary
consequences. No unrelated capability expansion.

### 9. Protected-file drift check — ONLY EXPECTED FILES TOUCHED

- `CLAUDE.md`: only §5's exemption clause changed (diffed directly) —
  expected, user-approved per §0.
- `decisions/*`: only `0064` is new; `0063` diffed empty (unedited) —
  expected.
- `.claude/agents/*.md`: only `roadmap-context-curator.md` touched
  (confirmed via `git diff --stat` restricted to that glob) — expected,
  no other agent file touched.

### 10. Commit hygiene — CLEAN

Read the full commit message body of all nine corrective-pass commits
(`feaaaa0`, `db33352`, `bb21122`, `6d668db`, `a89920d`, `48a5fea`,
`924bea5`, `0db424a`, `8ab36aa`). None contains an AI attribution
trailer or co-author line (`CLAUDE.md` §7).

### 11. Scratch-artifact check — CLEAN

`git worktree list` shows only the single primary worktree. `git status`
shows only the two learnings files (Finding 1) as modified — no other
untracked or stray files. No scratch directory related to this
corrective pass (or this audit's own live-CLI verification, which was
built and destroyed under the session scratchpad, outside the project
tree) was left behind.

## Verdict

**PASS WITH NON-BLOCKING OBSERVATIONS for the corrective work itself** —
all three defects are genuinely, completely fixed; tests, ruff, and both
doc-check scripts are clean; the drift audit is genuine and independently
verified; the retro addendum is substantive; documentation, ADR, and
cross-agent-doc consistency all hold; no scope creep, no unexpected
protected-file drift, no commit-hygiene issue, no scratch artifacts.

**One item blocks the terminal `done`-flip specifically and must be
resolved first:**

1. **Commit the `knowledge-curator` triage of `L-065`.** The triage
   content in `planning/learnings/inbox.md` (status: promoted,
   `promoted_to` field, substantive curation note) and the matching
   `planning/learnings/promoted.md` pointer line both currently exist
   only as uncommitted working-tree changes — not part of any commit
   through `8ab36aa`, the commit this audit was run against. Commit this
   as its own commit (per this project's established practice for a
   learnings-triage step) **before** dispatching the terminal
   `roadmap-context-curator` reconciliation — and note that, per
   `CLAUDE.md` §5's own newly-fixed exemption, this commit is explicitly
   outside the three-target exemption list, so it must land strictly
   before, not folded into, the terminal reconciliation commit. Once
   committed, no re-audit of this specific point should be needed (it is
   a pure landing of already-verified content, not a new change to
   audited behavior) — but the lead should confirm via `git diff --stat`
   that the commit touches only `planning/learnings/inbox.md` and
   `planning/learnings/promoted.md`, consistent with what was reviewed
   here.

No other finding rises to blocking. The corrective pass's substantive
engineering, documentation, and governance work is sound and verified
independently, end to end.
