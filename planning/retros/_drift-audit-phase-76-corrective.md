# Drift audit — Phase 76 corrective pass (post-reopen)

**Scope:** independent, per-phase docs-drift audit of the six-commit
corrective pass (`feaaaa0`..`924bea5`, HEAD `924bea5`) applied on top of
the original Phase 76 closeout (`b3abe07`). Governing doc:
`planning/v1-redefinition/documentation-lifecycle.md` §2.5. Checked
against real, current source (`src/codecompass/cli.py`,
`src/codecompass/git_topology.py`) and a live test run — not against any
commit message's own summary.

**Verdict: NO DRIFT.**

## What changed, verified against code

Diffstat for the corrective-pass range (`feaaaa0~1..HEAD`) touches 19
files; the current-truth docs among them are `README.md`,
`ai-docs/README.md`, `architecture/overview.md`,
`architecture/context-graph-schema.md`, `docs/cli-reference.md`, plus
`decisions/0064` (new ADR) and `src/codecompass/{cli.py,git_topology.py}`
(the ground truth).

### 1. Git-version claim (Git 2.5 → 2.7)

Grepped the entire repository (excluding `vendor/`, `.git/`) for `Git
2.5` / `git 2.5` / "requires Git" / "Git version" / minimum-version
phrasing. Findings, each read directly and checked against
`git_topology.py`'s real `_MIN_GIT_VERSION = (2, 7)` and
`_detect_git_version`/`detect_git_topology` gating logic:

- `README.md:157` — "Requires Git 2.7+." Correct.
- `ai-docs/README.md:49` — "Requires Git 2.7+ (`decisions/0064`)."
  Correct.
- `architecture/overview.md:788-796` — "Requires Git 2.7+
  (`decisions/0064`) — `--git-common-dir` itself only needs Git 2.5, but
  `git worktree list`/`git remote get-url` ... were first introduced in
  Git 2.7.0 ... A Git older than 2.7 is detected via a single `git
  --version` check and reported as `unavailable` with an explicit,
  version-naming reason, never a crash." Matches
  `_detect_git_version`/the `UNAVAILABLE` branch in
  `detect_git_topology` exactly (the real reason string is `"git {M}.{m}
  is older than the minimum version (2.7) required for repository
  topology detection (git worktree list / git remote get-url)"`).
  Correct.
- `architecture/context-graph-schema.md:163-169` — same nuanced
  "2.5 for `--git-common-dir`, 2.7 for the two other calls" phrasing,
  same "explicit, version-naming `git_topology_reason`" claim. Correct.
- `docs/cli-reference.md:232-236` — "Requires Git 2.7+ (`decisions/0064`;
  `--git-common-dir` itself only needs Git 2.5, but `git worktree
  list`/`git remote get-url` ... need 2.7) — an older Git surfaces as
  'Git topology could not be determined,' with an explicit
  version-naming reason, not a crash." Correct; the "Git topology could
  not be determined (\<reason\>)" text matches
  `cli.py::_render_topology`'s real `status == "unavailable"` branch
  verbatim.
- `src/codecompass/git_topology.py` docstring (lines 16-23) and the
  `_MIN_GIT_VERSION` comment block (lines 60-68) — both correctly state
  2.7 as the real floor, 2.5 as `--git-common-dir`'s own (insufficient)
  requirement, and cite `decisions/0064` as superseding `decisions/0063`
  point 8. Correct.

No other doc-directory location carries the wrong claim.
`.claude/skills/codecompass/SKILL.md` was checked and does not state a
Git version at all for `query topology` (no claim, so nothing to be
stale). The only remaining "Git 2.5" text anywhere outside
`decisions/0063`/`0064` (which are supposed to retain it, see §3 below)
is in three **non-current-truth** locations, all of which are either
already-correct nuanced phrasing or deliberately-preserved historical
text, not drift:
- `CHANGELOG.md:54` (the *original* Phase 76 `[Unreleased]` entry,
  written before the corrective pass): "Git ≥2.5-compatible plumbing
  only." This is the original, now-known-wrong claim, deliberately left
  untouched — the corrective-pass's own later entry
  (`CHANGELOG.md:242-256`) explicitly names it as one of the three
  things that "was wrong" and documents the correction there instead of
  editing history. This mirrors this project's `decisions/*` append-only
  convention and is a defensible, self-disclosing choice, not an
  oversight — flagging it here only so the lead is aware it exists,
  not as a drift finding (`CHANGELOG.md` is not one of §5's / this
  audit's current-truth doc categories).
- `planning/phase-76-git-repository-topology.md` and
  `planning/retros/phase-76-git-repository-topology.md` — both
  planning-history documents, both contain the original claim
  alongside explicit "Corrective-pass correction" annotations pointing
  at the real 2.7 floor. Not current-truth docs, not in scope, and
  self-correcting in context regardless.

### 2. CLI rendering behaviour (tri-state fix)

Read `src/codecompass/cli.py` directly: `_tri_state_label` (lines
951-962) renders `True`/`False`/`None` into three distinct strings, never
collapsing `None` into the `when_false` branch. `_render_topology` (lines
965-1034) calls it for exactly the three fields named in the corrective
commit — the current worktree's `is_dirty` (line 1000), a submodule's
`revision_matches_pin` (line 1022) and `child_is_dirty` (line 1031) —
producing `dirty`/`clean`/`unknown` and `matches pin`/`differs from
pin`/`comparison unresolved`. `--json` output (line 970-974) dumps the
raw `profile` dict unmodified, so the nullable facts pass through as
JSON `null`/`true`/`false` untouched, consistent with the changelog's
"`--json` output was already correct and needed no fix" claim.

`docs/cli-reference.md`'s added sentence ("Every one of these dirty/match
facts is nullable and rendered as one of three explicit states — never
collapsed into a false negative — `dirty`/`clean`/`unknown` for workspace
state, `matches pin`/`differs from pin`/`comparison unresolved` for the
pin comparison") matches this behaviour exactly, including the label set
verbatim.

`architecture/context-graph-schema.md`'s `git_worktrees`/`git_submodules`
table rows already correctly describe the underlying columns as
nullable and don't make any claim about CLI text rendering, so they
needed no change and have none — no drift there either way. No other
current-truth doc (architecture, ai-docs, README) describes `query
topology`'s text-rendering behaviour at this level of detail, so no
other location was implicated.

Ran the two directly-relevant test files against current HEAD as an
independent behavioural check (not trusting the corrective commit's own
"4 new regression tests" claim): `pytest tests/test_cli.py
tests/test_git_topology.py` — **117 passed**, 0 failed.

### 3. `decisions/0063` / `decisions/0064` append-only check

`git diff feaaaa0~1..HEAD -- decisions/0063-git-repository-topology-as-a-new-graph-capability.md`
is empty — `0063` was not touched by any corrective-pass commit; its
original (now-superseded) Git-2.5 claim at point 8 remains exactly as
written. `decisions/0064-git-2.7-not-2.5-is-phase-76s-real-minimum-version.md`
is the only new file in `decisions/` across the range (confirmed via the
full diffstat). This matches the append-only ADR convention (CLAUDE.md
§2) and `decisions/0064`'s own stated purpose of superseding point 8
without editing it.

### 4. General sweep

Full diffstat for the range: `.claude/agents/roadmap-context-curator.md`,
`CHANGELOG.md`, `CLAUDE.md`, `README.md`, `ai-docs/README.md`,
`architecture/{context-graph-schema,overview}.md`, `decisions/0064`
(new), `docs/cli-reference.md`, `planning/CONTEXT.md`,
`planning/ROADMAP.md`, `planning/agent-led-workflow.md`,
`planning/learnings/inbox.md`, `planning/phase-76-*.md`,
`planning/retros/phase-76-*.md`, `src/codecompass/cli.py`,
`src/codecompass/git_topology.py`, `tests/test_cli.py`,
`tests/test_git_topology.py`. Every current-truth doc in that list
(`README.md`, `ai-docs/README.md`, both `architecture/` files,
`docs/cli-reference.md`) was checked above and found accurate.
`CLAUDE.md`'s own §5 exemption text (reviewed per the user's framing that
it required explicit approval) reads as internally consistent with the
rest of §5 and doesn't misdescribe any system behaviour — not a "current
truth about the system" doc in this audit's sense, so not further
audited for drift, only read for sanity. No other current-truth doc
references `_render_topology`, `_tri_state_label`, `_detect_git_version`,
or the corrective pass's specific fixes in any way that could now be
wrong.

## Domain-claim staleness check (step 5)

`docs/domain/` exists. Grepped `docs/domain/**` for
`topology|git_topology|worktree|submodule` — the only hits
(`references.md`, `concepts/protocol.md`, `concepts/capability.md`) all
use "submodule" in the *reference-project git submodule* sense
(`decisions/0057`, the protocol client repo checked out as a
`git submodule`), unrelated to Phase 76's `git_topology.py`
worktree/submodule *detection feature*. None cites `git_topology.py`,
`cli.py`'s topology renderer, `decisions/0063`, or `decisions/0064`.
**No domain-claim staleness candidates from this corrective pass.**

## Scope note

Checked: every current-truth doc (`README.md`, `docs/**`,
`architecture/**`, `ai-docs/**`) plus `.claude/skills/codecompass/SKILL.md`
for the Git-version claim and the CLI tri-state rendering claim
specifically named in the corrective pass; `decisions/0063`/`0064` for
the append-only convention; the full corrective-pass diffstat for any
other current-truth-doc implication; live test execution of the two
directly-relevant test files as an independent behavioural check.

Not re-checked (out of scope for a corrective-pass drift audit, already
covered by the *original* Phase 76 drift audit at
`planning/retros/_drift-audit-phase-76.md`): the rest of Phase 76's
original surface (schema tables, `sync.py` wiring, credential
sanitisation, bare-repo handling, the "not yet indexed" state) — none of
that was touched by this six-commit corrective pass. `CHANGELOG.md`,
`planning/CONTEXT.md`, `planning/ROADMAP.md`,
`planning/phase-76-git-repository-topology.md`, and
`planning/retros/phase-76-git-repository-topology.md` were read for
context but are not this audit's current-truth-doc targets (§5's
docs-drift gate names `README.md`/`docs/`/`architecture/`/`ai-docs/`
only); the one item worth the lead's attention there is noted above
under §1 as a non-drift observation, not a finding.
