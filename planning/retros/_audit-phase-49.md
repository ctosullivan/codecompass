# Release-phase audit — Phase 49 (`dev-docs/` spec-doc coverage + "not found" disambiguation)

**Auditor:** `release-phase-auditor` (independent, read-only).
**Scope inspected:** uncommitted working tree (`git diff` / `git status`)
against `planning/phase-49-spec-doc-coverage-and-error-disambiguation.md`.

## Verdict: PASS WITH NON-BLOCKING OBSERVATIONS

Everything within this phase's own engineering scope (code, tests, docs,
drift audit, retro, learnings/context-gap triage, protected-file
boundaries, live evidence) independently re-verifies clean. The only
open items are the explicitly-disclosed, not-yet-run final-reconciliation
steps (`CHANGELOG.md`/`ROADMAP.md`/`CONTEXT.md`, and two placeholder
commit hashes) — these are real, required DoD conditions per `CLAUDE.md`
§5 and are **not yet satisfied**, but they are the `roadmap-context-curator`'s
known next step, not a defect in this phase's substance. Numbered list
of exactly what remains before the phase can be marked `done` is below.

## What I re-ran myself (not trusted from any summary)

1. **`pytest`** (full suite, twice — once broad, once targeted):
   - Full suite: `557 passed, 2 skipped in 156.34s` — matches the phase's
     own claim exactly.
   - `tests/test_spec_docs.py tests/test_cli.py`: `76 passed in 153.85s`
     — matches the drift audit's claimed count exactly.
2. **`ruff check .`** → `All checks passed!`
3. **`python scripts/check_user_docs.py --strict`** → `no findings`
   (exit 0).
4. **Live Ledgerkit smoke test**, re-run from scratch against the actual
   scratch clone (`/tmp/.../scratchpad/ledgerkit`), confirmed the CLI on
   `PATH` is this working tree's editable install
   (`python -c "import codecompass; print(codecompass.__file__)"` →
   `.../codecompass/src/codecompass/__init__.py`), then:
   - Deleted the clone's stale `context-graph.db` and re-synced
     (`codecompass sync --budget 0`; the $0 cap correctly aborted the
     one AI-enrichment batch before any API spend — matches "mechanical-
     only" claim in the retro).
   - Queried `doc_artifacts` directly: 41 `dev-docs/**` rows now present,
     including nested paths
     (`dev-docs/planning/core-redefinition/07-query-regex.md`).
   - `codecompass query relations dev-docs/hledger-compatibility.md` →
     honest empty "(none)" relations table, not "not found."
   - Same for the nested path → same honest-empty result.
   - `codecompass query relations totally-made-up-name-xyz.md` → plain
     `error: '...' not found in context-graph.db`, unchanged.
   - `codecompass query relations knowledge/DOMAIN_RULES.md` (a real,
     still-uncovered file outside `dev-docs/`, confirmed present via
     `find`) → the new disambiguated message: `exists as a file but was
     not detected as a spec/vendor doc ... check whether it's covered by
     spec_docs's glob coverage, then re-run sync`, exit code 1.
   All four claims in the phase's report hold up exactly as described,
   independently reproduced.
5. **Source diff read directly** (`git diff -- src/codecompass/spec_docs.py
   src/codecompass/cli.py`): `_DEFAULT_GLOBS` gained exactly one entry,
   `"dev-docs/**/*.md"`, appended after `"ai-docs/**/*.md"`. `cli.py`
   gained `_relations_not_found_error`, called only from
   `query_relations`'s `relations is None` branch (line ~844); confirmed
   via `grep` that the sibling `_not_found_error` call site for `query
   vendor` (line ~596) is untouched, and `query_symbol` never called
   `_not_found_error` at all (pre-existing, different message path) — the
   plan's "scoped to `query_relations` only" constraint holds exactly.
6. **Docstring-citation fix verified**: `grep -n "0051" src/codecompass/cli.py`
   → no hits. `_relations_not_found_error`'s docstring now correctly
   cites `CG-002`/`L-016`, GATE DB Phase 47 — the drift audit's flagged
   defect was genuinely fixed before this audit ran.
7. **Protected-file check**: `git diff --stat -- CLAUDE.md decisions/`
   → empty; `git status --porcelain -- CLAUDE.md decisions/` → empty. No
   drift.
8. **Scope-creep check**: `git status --porcelain=v1` file list matches
   the plan's Files section exactly: `src/codecompass/spec_docs.py`,
   `src/codecompass/cli.py`, `tests/test_spec_docs.py`, `tests/test_cli.py`,
   `docs/cli-reference.md`, `architecture/overview.md`, plus the
   curator/retro/drift-audit files the plan names as belonging to other
   agents. `ai-docs/README.md` (also named in the plan, conditionally)
   was correctly left untouched — grepped it for `dev-docs`/`_DEFAULT_GLOBS`/
   "not found"/"glob" and found no mention that the change would make
   stale. `planning/reference-projects/ledgerkit/findings.md` is
   correctly untouched (plan explicitly defers that append to Phase 51).
9. **Independent `docs-reconstructor` drift audit** exists at
   `planning/retros/_drift-audit-phase-49.md`, verdict `NO DRIFT`, and is
   itself substantive: it independently re-diffed the code, compared
   `_DEFAULT_GLOBS`'s enumeration in `architecture/overview.md` entry-by-
   entry, re-ran the targeted test files itself, checked the two sibling
   `_not_found_error` call sites for accidental staleness, did a reverse
   search for other docs that might now be silently false (found only
   pre-existing "etc."-elided lists, consistent with the Phase 37
   precedent), and is the source of the docstring-citation catch. This
   is exactly the kind of independent, from-scratch verification §5
   requires, not a rubber stamp.
10. **Retro** at `planning/retros/phase-49-spec-doc-coverage-and-error-
    disambiguation.md` checked section-by-section against
    `planning/retros/TEMPLATE.md`: every section present and substantive
    — "Where we are" gives real arc context (Stage C spending Stage B's
    evidence, first external-evidence-driven `src/` change), "What
    worked"/"What didn't work" are specific and honest (names the
    docstring-citation slip rather than omitting it), "Where we're
    going" correctly identifies Phase 51 (not 50, which GATE DB didn't
    fund) as the natural next step and states the trajectory is
    "confirmed." Not a stub.
11. **Learnings/context-gaps triage** read in full diff:
    - `CG-002`: status stays `promoted-to-roadmap` with a closing note
      confirming the fix landed, referencing the actual regression test
      and the live Ledgerkit re-check. This is a defensible reading of
      `context-gaps/README.md`'s status list (`candidate` → `recurred` →
      `promoted-to-roadmap` / `discarded`) — confirmed by reading the
      README directly: there genuinely is no more-terminal state defined
      for "the owning phase's fix has landed," so recording it as an
      annotation rather than inventing an undocumented status is correct,
      not an under-claim.
    - `L-016`: status line flipped `retained` → `promoted` (confirmed via
      `grep -n "^- \*\*status" planning/learnings/inbox.md`), with a
      `promoted_to:` block naming the actual landing site
      (`_relations_not_found_error` + both new tests) and a
      `planning/learnings/promoted.md` line added. Placeholder commit
      hash `TBD-this-phase-commit` used, matching the existing
      `L-011`/`L-013`/`L-018` convention in the same file (verified those
      three lines use real hashes already landed, so the convention is
      real, not invented for this phase).
    - Both triage notes state they independently re-read the actual code
      rather than trusting the phase's own report — consistent with
      `agent-led-development.md`'s "no agent observation is authoritative
      because an agent recorded it" discipline.

## Outstanding items (must be done before Phase 49 is `done`)

1. **`CHANGELOG.md`** has no `[Unreleased]` entry for Phase 49 yet (only
   Phase 47's entry is present). Required per `CLAUDE.md` §3/§5.
2. **`planning/ROADMAP.md`** line 334 still shows Phase 49 status
   `planned`, not `done`. Required per `CLAUDE.md` §2/§5.
3. **`planning/CONTEXT.md`** still describes Phase 49 as the "immediate
   next step" (lines ~309-310, ~976-977) rather than reflecting it as
   completed. Required per `CLAUDE.md` §4/§5.
4. **Two placeholder commit hashes** (`TBD-this-phase-commit`) in
   `planning/context-gaps/inbox.md`, `planning/learnings/inbox.md`, and
   `planning/learnings/promoted.md` need backfilling with the real
   closeout commit hash once it lands, per the disclosed
   `L-011`/`L-013`/`L-018` convention.
5. **The retro's own "Commit(s)" field** (`*(pending — this phase's
   closeout commit)*`) needs the same backfill once committed.

None of these are defects in the phase's engineering work — they are the
explicitly-disclosed, not-yet-run `roadmap-context-curator` reconciliation
step that this audit was invoked ahead of. They are real, required DoD
conditions, so the phase is not yet formally `done`, but nothing here
requires touching `src/`, tests, or the already-verified docs/drift-audit/
retro/triage work.

## Non-blocking observations

- None beyond the items above. The docstring-citation slip the drift
  audit caught was already fixed before this audit ran and is honestly
  recorded in the retro's "What didn't work" — no further action needed
  on it.
- This phase is not a reference-project phase itself (it's the fix, not
  a new evaluation), so a `context-evaluator` report is correctly not
  expected here (Phase 51 will need one).
