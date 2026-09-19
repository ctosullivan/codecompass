# Phase 61: hledger cross-language experiment — plan

**Status:** plan only, not started. Do not begin implementation until
this plan is reviewed (`CLAUDE.md` §1).

## 0. Why this phase, and why now

Stage F (`decisions/0056`), gated on nothing (a separate axis from Stage
E/GATE DD). Phase 60 just shipped the first real external CodeCompass
adapter and independently confirmed it works correctly against
`hledger-lib`. Phase 61 is Stage F's next phase, and its purpose was
narrowed twice before Phase 60 even existed:

- The original roadmap description: register `hledger`/`hledger-lib` as
  a real tracked vendor and evaluate whether that materially helps a
  real Ledgerkit task, the same way every prior reference-project phase
  has been evaluated (`context-quality-evaluation.md`'s instrument).
- **Refined by Phase 54b's own plan (§9)**, before Phase 60 existed: the
  central test is not "does the adapter parse Haskell" (that was Phase
  60's own DoD) — it is **whether CodeCompass helps an agent recognise
  that two differently-implemented things are the same behaviour**.
  Phase 54b's own real result is this phase's stated baseline: re-run
  the same `depth:`/`--depth` behavioural-reconstruction question,
  using real Haskell-side structural information (the new adapter)
  instead of Phase 54b's curated document/reference layer, and
  separately test whether CodeCompass helps relate that Haskell-side
  understanding to Ledgerkit's own Python reimplementation
  (`ledgerkit.query.depth.DepthSpec`, `clip_account_name`) as one
  behavioural concept realised in two languages.

**Phase 54b's own baseline, re-confirmed live this session** (not
assumed from the retro): both `/home/cormac/projects/hledger` (pinned
commit `33fa849e7ae841968bd21c427094c4fb4a4ec38d`, tag `1.52.4`) and
`/home/cormac/projects/ledgerkit` (`HEAD` `c6168b2`) are exactly where
Phase 54b's retro left them — nothing has drifted. Phase 54b's real
result: baseline (raw source, no CodeCompass) **PASS**; treatment
(CodeCompass's curated `dev-docs/hledger-reference/` ingestion) **PASS
WITH GAPS** — the curated set omitted `Stats.hs` entirely (a human
curation gap, not a detection defect, `OBS-014`), forcing a disclosed
fallback exactly where the task's one genuine exception lived. Context
advantage: **LOW**. This is the number Phase 61's own treatment
condition is measured against.

Ledgerkit's own real `depth:` behaviour, independently re-verified live
this session against `ledgerkit/query/depth.py`: `DepthSpec` (line 27)
and `clip_account_name` (line 159) both exist exactly as named in
`decisions/0057`'s own forward reference — nothing speculative here.

## 1. Current-state inspection (real, re-verified this session)

**Where the five real command implementations actually live — a fact
Phase 54b's own curation missed and this phase must not repeat**:
`balance`/`register`/`accounts`/`print` all resolve inside `hledger-lib`
(`Query`/`Depth`'s own definition, `Hledger/Query.hs`), but the *command*
files themselves — `Balance.hs`, `Register.hs`, `Accounts.hs`,
`Stats.hs`, `Print.hs` — live in the **sibling** `hledger` package
(`hledger/Hledger/Cli/Commands/*.hs`), confirmed directly:
```
$ find /home/cormac/projects/hledger -iname "Stats.hs" -o -iname "Balance.hs"
/home/cormac/projects/hledger/hledger/Hledger/Cli/Commands/Stats.hs
/home/cormac/projects/hledger/hledger/Hledger/Cli/Commands/Balance.hs
```
`hledger/hledger.cabal`'s own `exposed-modules` list confirms all five
command modules (`Hledger.Cli.Commands.{Accounts,Balance,Print,Register,Stats}`)
are genuinely exposed — the adapter's existing, unmodified export-list
scanner would already surface every one of them, mechanically and
exhaustively, the moment `hledger` is tracked as a second vendor
alongside `hledger-lib`. **This phase tracks both packages** —
`hledger-lib` alone would silently reproduce Phase 54b's own exact
`Stats.hs` gap, just one layer further down the stack.

**A real, disclosed pre-existing bug found during this phase's own
planning, not by Phase 60's own review** — confirmed live, not
theoretical:
```
$ codecompass sync hledger-lib   # scratch dir, hledger-lib symlinked in, as Phase 60's own e2e test did
synced hledger-lib@1.52.4
$ ls vendor/hledger-lib/src
azure-pipelines.yml  ...  hledger  hledger-lib  hledger-ui  hledger-web  ...
```
`HaskellAdapter.repository_url()` (added in Phase 60) resolves the
`github:` shorthand to a plain URL but never sets
`RepositoryLocation.subdirectory` — the exact field `decisions/0021`
already introduced for this precise scenario (an npm monorepo package).
Without it, `source_resolution.resolve_and_clone` (correctly, per its
own contract) clones the **whole** `simonmichael/hledger` repository and
treats the clone root as `hledger-lib`'s own source — so
`vendor/hledger-lib/src/` ends up containing `hledger`/`hledger-ui`/
`hledger-web` too, not scoped to `hledger-lib` at all. Real network
access is confirmed available in this environment
(`git ls-remote https://github.com/simonmichael/hledger.git HEAD`
succeeds), so this is not a theoretical failure path — it is exactly
what a real `codecompass sync` produces today. This must be fixed as
part of this phase: Phase 61's own treatment condition is invalid if the
agent's "real cloned vendor source" is actually an unscoped monorepo
dump. See §4.

**`usage.py`'s Haskell import detection — named as "Phase 61's own
scope" by `decisions/0057`/Phase 60's plan, re-examined here with real
evidence and reconciled, not silently dropped**: Ledgerkit's own Python
source cannot literally `import` Haskell code, so `usage.py`'s existing
per-ecosystem dispatch (`detect_imports_for_file`) has no application
inside *this* phase's own scratch project. The one place a Haskell
import genuinely occurs — `hledger`'s own vendored source
(`vendor/hledger/src/...`) importing `hledger-lib`'s modules — lives
inside the `vendor/` directory, which `usage.py`'s own project-source
walk already prunes unconditionally, by design (`resolve_project_usage`'s
own documented rationale: a vendor's own source referencing its own
package name would otherwise produce false-positive "the project uses
this" edges for nearly every vendor). The cross-vendor relationship that
actually matters here — "`hledger` depends on `hledger-lib`" — is
**already produced, with zero new code**, by the existing,
fully ecosystem-agnostic `build_depends_on_edges` (`doc_mapping.py`),
which flattens each tracked vendor's own `deptree.json` (already correct
for Haskell since Phase 60) and emits a `Vendor → Vendor` edge wherever
a flattened dependency name matches another tracked vendor — confirmed
by reading the function directly, not assumed. **Conclusion: this phase
does not implement Haskell import/call-site detection in `usage.py`** —
not because it's out of scope by fiat, but because real investigation
found no actual consumer for it inside this phase's own task, and the
one cross-vendor relationship that *is* relevant is already mechanically
correct today. Left genuinely unscheduled (not re-deferred to a specific
future phase) unless a real Haskell-*consuming*-project scenario
surfaces one — flagged in the review gate for visibility, since it
reverses a prior phase's own stated deferral target.

**`CG-008` (Phase 60's own finding, routed to Phase 62 — `symbols` table
stays empty for Haskell vendors) does not block this phase**: the
treatment condition's own context comes from the generated per-vendor
`CLAUDE.md` (`readme_and_api_surface()`, already correct, already proven
against the full real `hledger-lib` in Phase 60) plus the real cloned
source — never from a `codecompass query symbols` call. This mirrors
Phase 54b's own treatment methodology exactly: the agent works from
generated/indexed material, with a disclosed, allowed fallback to direct
source reading if that material proves insufficient.

## 2. Experiment design

Same overall shape as Phase 54b (§4 of that plan): a real, disposable
scratch copy, two independent fresh-agent dispatches on an identical
task, independent evaluation — extended one level, from "does the
document layer help" to "does real structural information from a live
external adapter help, including relating it across languages."

### 2.1 Setup (real, not curated)

A fresh scratch clone of Ledgerkit (`.../scratchpad/ledgerkit-scratch-61`,
never the real repository — matching every prior phase's own established
practice), re-pinned at its own real current `HEAD` at implementation
start (per this project's standing "reconfirm before use" discipline —
`c6168b2` as of this plan, subject to a live recheck). Inside that
scratch copy, a new `vendor.toml`:

```toml
[[vendor]]
name = "hledger-lib"
ecosystem = "haskell"

[[vendor]]
name = "hledger"
ecosystem = "haskell"
```

`HaskellAdapter.project_root` needs to resolve to the real, local
`hledger` monorepo checkout for both entries — the same
symlink-into-the-scratch-directory approach Phase 60's own e2e
validation already used and proved works (`hledger-lib` symlinked at
the scratch project's root; here, both vendor names resolve against the
same monorepo root via the existing, unmodified monorepo-search logic
in `HaskellAdapter._resolve_package_dir`). A real `codecompass sync
--yes --budget 0` (no AI spend — matching Phase 60's own real e2e
run) populates `vendor/hledger-lib/` and `vendor/hledger/` — real
digests, real (once §4's fix lands) correctly-scoped source clones, real
dependency trees, sitting inside the same scratch tree as Ledgerkit's
own `ledgerkit/` package source.

### 2.2 The task given to both runs

One combined task (not two separate dispatches per condition — the two
named goals are naturally one real behavioural-porting/compatibility
question, not two unrelated ones):

*"Determine hledger's actual `depth:`/`--depth` behaviour for the
`balance`, `register`, `accounts`, `stats`, and `print` commands, citing
concrete evidence for each. Then determine whether and how Ledgerkit's
own Python implementation (`ledgerkit/query/depth.py`) reproduces that
same behaviour — cite the specific functions on both sides, and state
explicitly any case where they diverge or where you cannot confirm
equivalence."* — the same first half as Phase 54b's own task (so the
two results are genuinely comparable), extended with the cross-language
half `decisions/0057`/Phase 54b's plan named as this phase's own real
addition.

### 2.3 Baseline run

A fresh agent, given: the pinned local `hledger` clone, the pinned local
`ledgerkit` clone, and ordinary tools (`Read`, `Grep`, `Bash`,
`WebFetch`) — **no CodeCompass**. Reproduces Phase 54b's own baseline
condition, extended to also have Ledgerkit's source in reach (Phase
54b's own baseline did not need it, since Phase 54b never asked the
cross-language question).

### 2.4 Treatment run

A fresh agent, given the scratch Ledgerkit copy **after** the real
`codecompass sync` above — the generated `CLAUDE.md` routing table,
`vendor/hledger-lib/`'s and `vendor/hledger/`'s own generated
`CLAUDE.md`/`DEPTREE.md`/`FILETREE.md` and real cloned source, plus
Ledgerkit's own unchanged `ledgerkit/` package. The treatment agent
works from this generated/indexed material first; a fallback to direct
source reading is allowed and is itself a recordable finding if used
(Phase 54's/54b's own precedent), not a disallowed move.

### 2.5 Independent evaluation

`context-evaluator`, dispatched fresh, re-deriving ground truth directly
from the real `hledger`/`ledgerkit` source (never from this plan's own
summary, never from either agent's own report) — the existing
`context-quality-evaluation.md` instrument, including Phase 54b's own
added "execution-path completeness" criterion (did either run miss a
command the way Ledgerkit's real Stage C Phase 1 once did?). Rates both
runs; the treatment rating, compared against Phase 54b's own **LOW**
baseline, is this phase's central result. `reference-project-tester`
files any real friction (missing/stale/incorrect relationships,
un-representable relationships) via the existing `context-gaps`/
`context-observations` queues — no new queue, no new ontology, matching
every prior phase's own "reuse existing mechanisms only" discipline
(Phase 54b §6).

## 3. What this phase deliberately does not build

- No new behavioural/claim ontology, execution graph, or relationship
  type. If the experiment finds CodeCompass's existing mechanisms
  (generated digests + real source + `depends_on_edges`) insufficient to
  even represent something real it found, that insufficiency is filed as
  a `CG-NNN`/`OBS-NNN` candidate for GATE DD to weigh later — not treated
  as license to build the missing thing inside this phase.
- No `usage.py` Haskell import/call-site detection (§1's own reasoning).
- No fix to `CG-008` (`_collect_vendor_symbols`'s own gap) — Phase 62's
  scope, unaffected here since this phase never depends on the graph's
  `symbols` table.
- No change to the external adapter itself
  (`codecompass-adaptor-haskell`) — its own real output is already
  sufficient for this phase's own task; the one fix this phase needs
  (§4) is entirely on the CodeCompass-core side.

## 4. The one required fix: `HaskellAdapter.repository_url()`'s missing `subdirectory`

`RepositoryLocation` already has a `subdirectory` field (`decisions/0021`,
used by the npm adapter today); `HaskellAdapter.repository_url()` simply
never sets it. Fix: when the resolved package directory
(`self._resolve_package_dir()`) differs from `self.project_root` (the
monorepo case), set `subdirectory` to the relative path between them —
mirroring exactly what the npm adapter already does for its own
monorepo case, no new mechanism, no interface change. `hledger-lib`'s
own case resolves to `subdirectory="hledger-lib"`; a non-monorepo
Haskell package (project root *is* the package) keeps `subdirectory=None`,
unchanged from today.

This is scoped narrowly to the one real defect this phase's own
real-world use actually surfaced — not a general audit of
`resolve_and_clone`/monorepo handling beyond what's needed here.

## Scope

**In scope:**

- Fix `HaskellAdapter.repository_url()` to set `RepositoryLocation.subdirectory`
  for a monorepo member (§4). New fixture test: a two-package synthetic
  monorepo (mirroring `test_monorepo_resolves_to_matching_subdirectory`'s
  existing fixture shape) asserting `repository_url().subdirectory ==
  "hledger-lib"`; a non-monorepo case asserting `subdirectory is None`
  (regression guard for the existing behaviour).
- A disposable scratch Ledgerkit copy
  (`.../scratchpad/ledgerkit-scratch-61`), never the real repository, with
  a new `vendor.toml` tracking `hledger-lib` and `hledger` (both
  `ecosystem = "haskell"`).
- A real `codecompass sync --yes --budget 0` against that scratch copy —
  real digests, real (correctly-scoped, post-§4-fix) source clones, real
  dependency trees for both vendors.
- Two fresh-agent dispatches (baseline, treatment) on the combined task
  (§2.2), each independent of this planning conversation and of each
  other.
- Independent `context-evaluator` rating (§2.5) against Phase 54b's own
  **LOW** baseline, using the unchanged existing instrument.
- `reference-project-tester` friction filing via the existing
  `context-gaps`/`context-observations` queues.
- A written evaluation report under
  `planning/reference-projects/ledgerkit/` (mirroring
  `02-depth-behavioural-reconstruction-evaluation.md`'s own shape — this
  becomes `03-...`).
- The explicit reconciliation of `usage.py`'s Haskell-import-detection
  deferral (§1) — a documented scope decision, not code.
- Standard phase closeout: retro, `knowledge-curator` triage of any
  candidate learnings/gaps, `release-phase-auditor`, `docs-reconstructor`
  drift audit only if `src/`/current-truth docs change (the §4 fix does
  touch `src/`, so this audit runs).

**Explicitly deferred / out of scope:**

- `usage.py`'s Haskell import/call-site detection (§1, §3) — genuinely
  unscheduled, not merely postponed to a named future phase.
- `CG-008` (`_collect_vendor_symbols`'s own gap) — Phase 62.
- Any change to `codecompass-adaptor-haskell`/`codecompass-adaptor-protocol`
  (the two separate repositories) — this phase's own findings are
  CodeCompass-core-side only.
- A general audit of `resolve_and_clone`/monorepo handling beyond the
  one real Haskell case this phase needs (§4's own scoping note).
- Any new behavioural ontology, claim system, or relationship type (§3).
- Registering `hledger-ui`/`hledger-web` (the two remaining monorepo
  siblings) — not needed for the `depth:` task's own five commands, and
  adding them would not change this phase's own result.
- Resolving GATE DD, or completing/bypassing Phases 55-59 — unaffected
  by this phase, exactly as Phase 60 left them.

## Design decisions

- **Track both `hledger-lib` and `hledger`, not `hledger-lib` alone** —
  the five real command implementations the task asks about live in
  `hledger`, not `hledger-lib`; tracking only the latter would silently
  reproduce Phase 54b's own exact `Stats.hs` gap one layer down.
- **Fix the monorepo-clone-scoping bug now, as a small, narrowly-scoped
  in-phase prerequisite, not a separate phase** — Phase 61's own
  treatment condition is invalid without it (an agent reading a
  `vendor/hledger-lib/src/` that's secretly the whole monorepo is not a
  fair test of "real, correctly-scoped structural information"), and the
  fix reuses `decisions/0021`'s own existing mechanism verbatim — no new
  design surface.
- **One combined baseline/treatment task, not two** — the
  Haskell-reconstruction half and the cross-language-relation half are
  one real behavioural-porting question in practice; splitting them into
  separate dispatches would double agent-dispatch cost for a
  methodologically weaker (less realistic) test.
- **`usage.py` Haskell import detection is not built, and not
  re-deferred to a named future phase** — real investigation (§1) found
  no actual consumer for it inside this phase's own task and no
  near-term one either (the one cross-vendor relationship that matters
  is already mechanically correct via `depends_on_edges`); naming a
  future phase for it now would be exactly the "designing for a
  hypothetical requirement" this project's own discipline warns against.
- **No new ontology/mechanism regardless of what the experiment finds**
  — matching Phase 54b's own explicit constraint; any real
  representation gap becomes a `CG-NNN`/`OBS-NNN` filing for GATE DD, not
  a build trigger inside this phase.

## Files

- `src/codecompass/adapters/haskell.py` — `repository_url()` gains
  `subdirectory` resolution (§4).
- `tests/test_adapter_haskell.py` — two new fixture tests (monorepo
  subdirectory set; non-monorepo case unchanged at `None`).
- `.../scratchpad/ledgerkit-scratch-61/` (new, disposable, not committed
  to any repository) — the scratch Ledgerkit copy, its own new
  `vendor.toml`, and the real `codecompass sync` output.
- `planning/reference-projects/ledgerkit/03-hledger-cross-language-evaluation.md`
  (new) — the independent evaluation report.
- `planning/context-gaps/inbox.md` / `planning/context-observations/` —
  any real friction `reference-project-tester` files.
- `planning/learnings/inbox.md` — any candidate learnings (e.g. the §4
  bug itself is a strong learning candidate: "a new ecosystem adapter's
  `repository_url()` must set `subdirectory` for any monorepo member, or
  `resolve_and_clone` silently clones the wrong scope" — a generalisable
  point for *any* future adapter, not just Haskell).
- `planning/retros/phase-61-hledger-cross-language-experiment.md` (new)
  — the retro.
- `planning/ROADMAP.md`, `planning/v1-redefinition/roadmap.md`,
  `planning/CONTEXT.md`, `CHANGELOG.md` — updated at closeout, same
  commit discipline as every phase.

## Verification

- `pytest`/`ruff check .`/`check_user_docs.py --strict` all clean.
- The two new `repository_url()` fixture tests pass; a real, live
  re-run of the exact `codecompass sync` transcript in §1 confirms
  `vendor/hledger-lib/src/` now contains only `hledger-lib`'s own real
  files (its own `.cabal`, `Hledger/`, etc.) — no `hledger`/`hledger-ui`/
  `hledger-web` siblings — checked directly, not assumed from the fixture
  test passing.
- A real `codecompass sync --yes --budget 0` against the scratch
  Ledgerkit copy succeeds for both vendors, producing real,
  independently-inspected `CLAUDE.md`/`DEPTREE.md`/`FILETREE.md` content
  for each (not just "sync exited zero").
- `depends_on_edges` (or a direct `context-graph.db` query) shows a real
  `hledger → hledger-lib` edge once both are synced and the graph is
  rebuilt — confirming the "no new code needed for cross-vendor
  relationships" claim in §1 rather than merely asserting it.
- Both agent dispatches (baseline, treatment) are genuinely fresh, with
  no memory of this planning conversation (Phase 54b's own §4.1
  discipline, restated: the lead, having read Ledgerkit's own source to
  write this plan, must not be either agent under test).
- `context-evaluator`'s independent report exists, uses the unchanged
  instrument, and states the treatment condition's context-advantage
  rating explicitly against Phase 54b's own **LOW** baseline — a LOW or
  null result here is treated as valid evidence, not a phase failure,
  matching every prior phase's own posture.
- `release-phase-auditor` PASS or PASS WITH NON-BLOCKING OBSERVATIONS.

## Done when

Standard DoD (`CLAUDE.md` §5) + the `repository_url()` fix is real,
tested, and independently confirmed to produce a correctly-scoped real
clone (not merely a passing unit test) + both fresh-agent dispatches
completed and independently evaluated + the evaluation report explicitly
answers the two questions this phase exists to answer: (1) how does
real Haskell-side structural information compare to Phase 54b's
document-ingestion layer for the *same* `depth:` question (LOW/MODERATE/
HIGH, against Phase 54b's own LOW), and (2) did CodeCompass help the
treatment agent recognise hledger's and Ledgerkit's `depth:` handling as
the same behavioural concept realised in two languages, or not + any
real friction filed and triaged + retro states plainly whether tracking
a second, differently-licensed-ecosystem vendor as ordinary CodeCompass
content (digests, source clones, dependency edges) held up at real use,
not just at the single-vendor scale Phase 60 exercised.

**Not done merely because both agents produced a plausible-sounding
answer** — done only once `context-evaluator`'s independent, ground-truth-
verified rating exists and the LOW/MODERATE/HIGH comparison against
Phase 54b's own baseline is stated honestly, including if the result is
another LOW or a null result.

---

## Review gate

Presented for review before implementation starts.

1. **Tracking both `hledger-lib` and `hledger`** (not `hledger-lib`
   alone) — a judgment call made during this planning pass, not a direct
   instruction; flagged for visibility since it doubles the real network
   clone cost (§1's own disclosed, pre-existing, accepted inefficiency
   for monorepo siblings sharing one repository URL) and widens this
   phase's own real footprint slightly beyond the roadmap's original
   one-line "track hledger-lib" framing.
2. **Fixing `HaskellAdapter.repository_url()`'s missing `subdirectory`
   inside this phase**, rather than filing it as a `CG-NNN`/deferring it
   to Phase 62 — a real bug in already-shipped, already-tagged Phase 60
   code, found during this phase's own planning (§1), not by Phase 60's
   own review or its `release-phase-auditor` pass. Judged in-scope here
   because Phase 61's own treatment condition is invalid without it and
   the fix is small and mechanism-reuse-only — flagged explicitly since
   "fix a bug found in a already-released, tagged dependency" is exactly
   the kind of decision this project's own discipline says shouldn't be
   made silently.
3. **Not building `usage.py`'s Haskell import detection, and not
   re-deferring it to a named phase** — reverses `decisions/0057`'s own
   stated "Phase 61's own scope" language based on real investigation
   done during this planning pass (§1); flagged since it changes what a
   prior phase's own plan said would happen here.
4. **One combined baseline/treatment task covering both of Phase 54b's
   named goals**, rather than two separate dispatches per goal — a
   methodology choice, not a direct instruction.
5. **The scratch Ledgerkit copy's own re-pin to a live-reconfirmed
   `HEAD` at implementation start** — already checked once during this
   planning pass (`c6168b2`, unchanged since Phase 54b), but the plan
   itself doesn't re-verify this a second time at actual implementation
   start, per this project's own standing discipline — named here so
   implementation doesn't skip that step because this plan already
   looks like it did the checking.
