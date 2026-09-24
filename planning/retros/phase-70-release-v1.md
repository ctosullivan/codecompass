# Phase 70 retro — Release redefined CodeCompass v1

- **Date:** 2026-09-24
- **Commit(s):** `c70cbc3` (plan + ROADMAP row), `9dba747` (version
  bump + CHANGELOG flatten), `4d3a4f2` (PyPI distribution rename to
  `codecompass-context`, mid-phase user amendment), tag `v1.0.0`.
- **Agents used:** none — this phase's own irreversible action is the
  lead's own direct work, per the plan's own dispatch strategy.

## Where we are

Stage G's seventh and final phase — the actual, irreversible release
this entire redefined-v1 effort (39 phases, `decisions/0048` through
this one) has been building toward. `G2-b` held every prior phase back
from this exact point.

## Goal

Drop `.dev0`, build and verify the real distribution, publish to PyPI,
tag `v1.0.0`, and flatten `CHANGELOG.md`'s `[Unreleased]` into a dated
release section — only after the actual user's own explicit go-ahead.

## Scope delivered vs planned

Delivered with one real, user-directed mid-phase amendment: after the
plan's own pre-flight and build/verify steps completed, but before the
first upload attempt, the user asked to rename the PyPI distribution
from `codecompass` to `codecompass-context`, keeping the product name,
Python import package, and CLI command as `codecompass`. Applied
directly (a one-line `pyproject.toml` change — distribution name and
import name are already independent concepts in Python packaging),
rebuilt, re-verified via direct wheel-metadata inspection (not just
trusting `twine check`'s own PASSED result), and two live documentation
references to the old install command were fixed as a direct,
necessary consequence of the same rename (not scope creep — leaving
`docs/quickstart.md` telling a v1.0.0 user to `pip install codecompass`
when the real published name is `codecompass-context` would ship a
real, immediately-broken instruction).

## What was achieved

CodeCompass is published: `codecompass-context` 1.0.0 on PyPI (license
`GPL-3.0-or-later`, both wheel and sdist present) — confirmed via the
real PyPI JSON API, not merely a locally-reported upload success. The
`v1.0.0` git tag exists and is pushed to `origin`. `CHANGELOG.md`'s
`[Unreleased]` — ~40 per-phase subsections accumulated across the
entire effort — is now a dated `[1.0.0]` section in canonical
Keep-a-Changelog grouping, done mechanically and verified
byte-for-byte content-preserving before being applied to the real
file.

## What worked

- **A credential-isolation constraint was discovered and handled
  correctly, not worked around unsafely.** Neither shell environment
  variables nor a `~/.pypirc` file bridged from the user's own
  interactive `!` shell into this agent's own tool environment. Rather
  than ask the user to paste a raw token into the visible conversation
  (which very nearly happened once, by accident, and was flagged), the
  actual upload was handed to the user's own shell where credentials
  already worked — the token never needed to enter this agent's own
  context at all. This is the correct posture for exactly this class
  of constraint, not a workaround to route past it.
- **Sequencing build/verify before upload, and upload before tagging**
  (named explicitly in the plan's own §5) worked as intended: the
  build was fully verified in a clean scratch install (including
  working around this environment's own restricted network access to
  `files.pythonhosted.org` by reusing already-verified dependency
  packages, rather than skipping verification) before anything
  irreversible happened, and the tag was created only after the real
  PyPI listing was independently confirmed live.
- **Treating the mid-phase rename request as a plan amendment, not a
  new phase**, matched this project's own established precedent
  (Phase 60–62's own mid-execution amendments) — a real, well-scoped,
  user-directed correction folded into the phase already in progress
  rather than over-formalized into its own roadmap entry.
- **The mechanical CHANGELOG-flatten script, verified against a
  scratch copy with an exact line-count reconciliation before being
  applied to the real file**, avoided the real risk of silently
  dropping or duplicating content while reorganizing ~2400 lines
  accumulated across dozens of phases by hand.

## What didn't work

A secret value was typed directly into the visible conversation once
(the user's own PyPI token, via a malformed `export` command with a
stray space) before the credential-isolation constraint was fully
understood. No misuse occurred and the user was advised to rotate the
token as a precaution, but the ideal sequence would have been
confirming the isolation constraint *before* asking the user to type
credentials via `!` at all, rather than discovering the constraint
only after the first attempt.

## Lessons learnt

**Verify that a proposed credential-passing mechanism actually bridges
between the user's own interactive shell and this agent's own tool
environment before asking the user to use it** — a quick, harmless
check (e.g. `echo $SOME_TEST_VAR` after asking the user to export it)
would have caught the isolation immediately, before any real credential
was typed into the visible conversation. Left for `knowledge-curator`'s
own independent triage rather than the lead filing it unilaterally, per
this project's now-standard practice.

## Process-improvement feedback

None beyond the lesson above.

## Candidate learnings filed

None directly by the lead — the credential-verification lesson above
is described but deliberately left for `knowledge-curator`'s own
independent assessment of whether it's promotable.

## Where we're going

**This is the last planned phase of the redefined-v1 effort.**
`decisions/0048` through Phase 70 constitute one complete milestone
group, per `CLAUDE.md` §6 — the version tag now exists. Post-v1 work
(GATE DD/Stage E if ever funded, Phases 24/25/48/50 if ever revisited,
ordinary feature development) proceeds under the same agent-led model,
methodology, and governance this effort built and validated, but is no
longer part of a "redefined v1" milestone group — it is simply
CodeCompass's own ongoing development from here.

## Time / cost note

No agent dispatches — direct lead work throughout (build, verification,
the mechanical changelog script, the rename, the tag). One clean-venv
install worked around this environment's own network restriction by
reusing already-verified dependency packages rather than a full
fresh download.
