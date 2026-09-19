# Phase 61: hledger cross-language experiment — plan

**Status:** plan only, not started. Do not begin implementation until
this plan is reviewed (`CLAUDE.md` §1).

**Amended 2026-09-19** (direct user instruction, before implementation
began — this amendment strengthens methodology only; scope and
experiment design are preserved unchanged from the original plan below,
not replaced): four real gaps in the original methodology are closed —
(1) baseline and treatment inputs are now made **exactly symmetric**
(identical commit hashes, identical underlying source bytes, identical
tools, identical task wording — §2.1a), closing a real risk this
amendment's own investigation found: `resolve_and_clone` has no
commit-pinning support, so without an explicit fix the treatment
condition's own "real cloned vendor source" could silently be a
*different, newer* revision of `hledger` than the baseline's pinned
local checkout; (2) the evaluation is now explicitly **two-part plus
overall** — Part 1 (`depth:` behavioural reconstruction) and Part 2
(cross-language equivalence recognition) are scored, and reported,
separately as well as combined (§2.6); (3) CodeCompass's own real
contribution is now explicitly measured, not just asserted — which
generated artifacts the treatment agent actually used, what direct-source
reading remained necessary despite them, and whether that reduced
rediscovery relative to baseline, all logged by both agents themselves
using an identical, required report structure (§2.7); (4) the boundary
this phase does **not** cross — no graph-level Haskell symbol/usage
integration, since `CG-008` (Phase 60's own finding) leaves
`context-graph.db`'s own `symbols` table empty for any Haskell vendor —
is restated more prominently (new §1.5) and threaded through Scope,
Verification, and Done-when, so a PASS here is never mistaken for "the
graph understands Haskell," only "the adapter's own context, dependency
structure, and vendor-source grounding help." The planned
`HaskellAdapter.repository_url()` monorepo-subdirectory fix (§4) stays
in scope unchanged — this amendment's own symmetric-source-snapshot
requirement (§2.1a) depends on it even more directly than the original
plan did, since a wrongly-scoped clone would also break commit-pinning
verification.

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

## 1.5 What this experiment tests, and what it deliberately does not (amendment)

Stated explicitly and prominently, not left implicit inside §1's own
`CG-008` paragraph, since it governs how every result below must be
interpreted:

**This experiment tests**: (a) **adapter-derived context** — the real
symbol lists/purposes/`[reexport]`/`[undetermined]` markers
`readme_and_api_surface()` renders into each vendor's own `CLAUDE.md`,
already proven correct in Phase 60; (b) **dependency structure** — the
real `hledger → hledger-lib` relationship, both in each vendor's own
`DEPTREE.md`/`deptree.json` and as a real `Vendor → Vendor`
`depends_on_edges` graph row; (c) **vendor-source grounding** — a real,
correctly-scoped (post-§4-fix) local copy of each vendor's own actual
source, available for direct reading exactly where the generated digest
runs out.

**This experiment does not test**: graph-level Haskell *symbol*
integration — `context-graph.db`'s own `symbols` table stays at zero
rows for any Haskell vendor until `CG-008` is resolved (Phase 62's own
scope, deliberately unaffected here). Concretely: `codecompass query
symbols hledger-lib` (or any `query` subcommand reading the `symbols`/
`uses_edges` tables) returns nothing useful for either vendor in this
phase, by design, not by an oversight this phase should chase. If either
agent tries such a command and gets nothing back, that is an *expected*,
already-understood limitation — worth noting in a report if it happens,
not a new finding to investigate. A PASS or HIGH rating in this phase's
own evaluation reflects (a)-(c) above working well; it is never evidence
that (or a proxy for) graph-symbol integration itself is unnecessary or
already solved.

## 2. Experiment design

Same overall shape as Phase 54b (§4 of that plan): a real, disposable
scratch copy, two independent fresh-agent dispatches on an identical
task, independent evaluation — extended one level, from "does the
document layer help" to "does real structural information from a live
external adapter help, including relating it across languages." **This
amendment adds**: an explicit symmetry protocol (§2.1a), a required,
identical self-report structure for both agents (§2.7), and a two-part-
plus-overall scoring structure (§2.6) — the underlying setup/task/roles
are otherwise unchanged from the original plan.

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

### 2.1a Symmetry protocol (amendment)

The only intended difference between the two conditions is **the
CodeCompass-produced context available to the treatment**. Everything
else — commit hashes, underlying source bytes, tool access, task
wording — must be identical, verified, and recorded, not merely assumed
equal because both conditions start from "the pinned checkout."

- **Commit hashes, recorded before either agent is dispatched**: the
  exact `hledger` commit (re-confirmed live at implementation start,
  `33fa849e7ae841968bd21c427094c4fb4a4ec38d` as of this plan) and the
  exact `ledgerkit` commit (`c6168b2` as of this plan) both go verbatim
  into the task text itself (§2.2) and into the evaluation report's own
  "Setup" section — neither agent should ever be in doubt about which
  revision it's reasoning about.
- **A real, disclosed risk this amendment's own investigation found,
  and its mitigation**: `source_resolution._git_clone` (used by
  `resolve_and_clone`, which `codecompass sync` calls for every
  vendor's own `vendor/<name>/src/` snapshot) does a plain shallow clone
  of whatever the upstream repository's *current* default-branch head
  is — it has no commit-pinning support. Left unmitigated, the
  treatment's own `vendor/hledger-lib/src/`/`vendor/hledger/src/` could
  silently be a *different, newer* revision of `hledger` than the
  baseline's own pinned local checkout, quietly breaking the "only
  intended difference" invariant above. Mitigation (an experiment-setup
  step, not a `codecompass` behaviour change — no ref-pinning is added
  to `resolve_and_clone` itself, matching this project's own "smallest
  justified fix" discipline): immediately after `codecompass sync`,
  explicitly check each vendor's own cloned commit
  (`git -C vendor/hledger-lib/src rev-parse HEAD`, same for
  `vendor/hledger/src`) against the recorded pinned SHA; if it differs
  (likely, given real time has passed since the pin), check out the
  exact pinned commit inside that clone directly
  (`git -C vendor/hledger-lib/src checkout <sha>`) before either agent
  is dispatched. This guarantees the treatment agent's own raw,
  fallback-readable source is byte-identical to the baseline's, at the
  same recorded commit — verified via `git rev-parse HEAD` equality
  after the checkout, not assumed. The scratch Ledgerkit copy
  (`ledgerkit-scratch-61`) gets the same treatment: its own `HEAD` is
  checked against the real local `/home/cormac/projects/ledgerkit`
  checkout's own `HEAD` and reset to match if it has drifted, before
  either agent starts.
- **Identical tools**: both agents get the same base toolset (`Read`,
  `Grep`, `Bash`, `WebFetch`) and the same filesystem access pattern
  (both can reach the real pinned `hledger`/`ledgerkit` checkouts
  directly if they choose to, regardless of condition) — the treatment
  agent's own working directory *additionally* contains the
  `codecompass`-generated material (§2.4); nothing is removed or
  restricted for either side to manufacture a cleaner contrast.
- **Identical task wording**: the exact same task string (§2.2,
  including the now-embedded commit hashes) is given to both agents,
  copy-pasted, never paraphrased differently per condition.
- **Recorded, not just asserted**: the evaluation report's own "Setup"
  section quotes the exact recorded commit hashes, confirms (with the
  real `git rev-parse HEAD` output) that the treatment's vendor source
  and the baseline's local checkout matched at dispatch time, and quotes
  the identical task string both agents received.

### 2.2 The task given to both runs

One combined task (not two separate dispatches per condition — the two
named goals are naturally one real behavioural-porting/compatibility
question, not two unrelated ones), given **verbatim identically** to
both agents (§2.1a):

*"hledger is pinned at commit `33fa849e7ae841968bd21c427094c4fb4a4ec38d`
(tag `1.52.4`); Ledgerkit is pinned at commit `c6168b2` (both
re-confirmed live immediately before this task was given to you — if
your own checkout disagrees, stop and say so before proceeding).*
*Part 1: Determine hledger's actual `depth:`/`--depth` behaviour for the
`balance`, `register`, `accounts`, `stats`, and `print` commands, citing
concrete evidence for each. State explicitly whether the behaviour is
uniform across all five commands or varies, and why.*
*Part 2: Determine whether and how Ledgerkit's own Python implementation
(`ledgerkit/query/depth.py`) reproduces that same behaviour — cite the
specific functions on both sides, and state explicitly any case where
they diverge or where you cannot confirm equivalence.*
*Report section 3 (required, both parts): list every file you actually
read (generated or raw source) and, for each, one line on why you
needed it."* — Part 1 is the same question as Phase 54b's own task (so
the two results are genuinely comparable); Part 2 is the cross-language
half `decisions/0057`/Phase 54b's plan named as this phase's own real
addition; the closing "list every file you read" requirement is this
amendment's own addition (§2.7), asked of **both** agents identically so
a real rediscovery comparison is possible, not just a treatment-side
self-report with nothing to compare it against.

### 2.3 Baseline run

A fresh agent, given: the pinned local `hledger` clone, the pinned local
`ledgerkit` clone, and ordinary tools (`Read`, `Grep`, `Bash`,
`WebFetch`) — **no CodeCompass**. Reproduces Phase 54b's own baseline
condition, extended to also have Ledgerkit's source in reach (Phase
54b's own baseline did not need it, since Phase 54b never asked the
cross-language question). Per §2.1a, the exact same commit hashes named
in the task text are what this agent's own checkouts are actually at,
verified before dispatch.

### 2.4 Treatment run

A fresh agent, given the scratch Ledgerkit copy **after** the real
`codecompass sync` above and after §2.1a's own commit-pinning
verification/checkout step — the generated `CLAUDE.md` routing table,
`vendor/hledger-lib/`'s and `vendor/hledger/`'s own generated
`CLAUDE.md`/`DEPTREE.md`/`FILETREE.md` and real, commit-pinned cloned
source, plus Ledgerkit's own unchanged `ledgerkit/` package — identical
tool access to the baseline (§2.1a), with this generated material simply
present in the working directory. The treatment agent works from this
generated/indexed material first; a fallback to direct source reading is
allowed and is itself a recordable finding if used (Phase 54's/54b's own
precedent, and now a *required*, not optional, part of its own report —
§2.7), not a disallowed move.

### 2.5 Independent evaluation

`context-evaluator`, dispatched fresh, re-deriving ground truth directly
from the real `hledger`/`ledgerkit` source (never from this plan's own
summary, never from either agent's own report) — the existing
`context-quality-evaluation.md` instrument, including Phase 54b's own
added "execution-path completeness" criterion (did either run miss a
command the way Ledgerkit's real Stage C Phase 1 once did?), applied
**per §2.6's two-part-plus-overall structure**, not as one undifferentiated
rating. `reference-project-tester` files any real friction
(missing/stale/incorrect relationships, un-representable relationships)
via the existing `context-gaps`/`context-observations` queues — no new
queue, no new ontology, matching every prior phase's own "reuse existing
mechanisms only" discipline (Phase 54b §6).

### 2.6 Two-part-plus-overall scoring (amendment)

A single undifferentiated verdict cannot distinguish "CodeCompass helped
find the right files but didn't help relate the two languages" from the
reverse, or from "helped with both," or "helped with neither" — four
genuinely different, actionable outcomes this phase exists to tell apart.
`context-evaluator`'s report therefore carries **three** verdict blocks,
each using the unchanged `context-quality-evaluation.md` criteria table
(accuracy/relevance/completeness/freshness/grounding/noise/safety) plus
execution-path completeness, applied to that block's own scope:

- **Part 1 — `depth:` behavioural reconstruction** (the hledger-only
  half): verdict (PASS/PASS WITH GAPS/FAIL) + context advantage
  (LOW/MODERATE/HIGH) for *this half alone*, directly comparable to
  Phase 54b's own real result (treatment: PASS WITH GAPS, LOW).
- **Part 2 — cross-language equivalence recognition** (the
  hledger-to-Ledgerkit relation half): its own verdict + context
  advantage, independently rated — a real, separate question, since
  correctly reconstructing hledger's own behaviour (Part 1) does not by
  itself guarantee an agent correctly relates it to Ledgerkit's own,
  differently-structured Python code.
- **Overall**: a combined verdict/advantage plus one required sentence
  naming which of the four outcome shapes actually occurred: (a) helped
  both parts; (b) helped Part 1 (navigation/reconstruction) but not
  materially Part 2 (cross-language semantic recognition); (c) the
  reverse; (d) helped neither. **(b) is the specific outcome shape this
  amendment was written to make legible** — the original plan's own
  single-verdict design could not have distinguished it from (a).

### 2.7 CodeCompass contribution measurement (amendment)

Required of **both** agents' own final reports (not treatment-only —
without a baseline number, "the treatment used N generated artifacts"
has no comparator):

- **Artifacts/files consulted**: the literal list each agent's own task
  response already has to produce (§2.2's closing requirement) — for the
  treatment, split into *generated* (which `CLAUDE.md`/`DEPTREE.md`/
  `FILETREE.md`, which vendor) vs *raw source* (which real `.hs`/`.py`
  file, read directly despite generated material being available).
- **Direct-source investigation that remained necessary despite
  generated context** (treatment only, since baseline has no generated
  context to fall back from): named explicitly, not inferred after the
  fact — matches Phase 54b's own "a disclosed fallback is itself a
  recordable finding" precedent, now a required report field rather
  than something that only surfaces if the agent happens to mention it.
- **Rediscovery comparison** (computed by `context-evaluator`, not
  self-reported by either agent, to keep it independent): given both
  agents' own file lists, does the treatment's list show it *skipped*
  real investigation the baseline had to do (a raw source file the
  baseline read directly that the treatment's own generated digest
  already answered), or does the treatment's list show it read
  essentially the same raw files as the baseline *in addition to* the
  generated material (meaning the generated material added noise/reading
  overhead without reducing rediscovery)? Reported as one of: **reduced
  rediscovery** (treatment needed fewer/no direct reads for information
  the generated material already supplied), **no measurable reduction**
  (treatment read comparably to baseline despite having generated
  material available), or **increased overhead** (treatment spent
  material effort reading generated content that didn't end up
  mattering). This is the concrete, checkable answer to "did CodeCompass
  actually save real work," not a proxy inferred from the verdict alone.

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
- **(Amendment) No general commit-pinning/ref-parameter support added to
  `resolve_and_clone`** — the real symmetry gap §2.1a found is worked
  around for this one experiment via a manual post-sync checkout in its
  own scratch directories, not by building a general reproducible-clone
  feature this phase doesn't otherwise need.
- **(Amendment) No graph-level Haskell symbol/usage integration** — see
  §1.5; `CG-008` stays Phase 62's own open question.

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
- **The symmetry protocol (§2.1a, amendment)**: recorded, verified
  commit hashes for both `hledger` and `ledgerkit`; a post-sync
  commit-pinning check-and-checkout step for both vendor source clones
  and the scratch Ledgerkit copy itself; identical tool access and task
  wording for both agents.
- Two fresh-agent dispatches (baseline, treatment) on the combined,
  two-part task (§2.2), each independent of this planning conversation
  and of each other, each required to report which files it read and
  why (§2.7, amendment — now required of **both** agents, not
  treatment-only).
- Independent `context-evaluator` rating, structured as **two parts plus
  an overall verdict** (§2.6, amendment) against Phase 54b's own **LOW**
  Part-1 baseline, using the unchanged existing instrument applied
  per-part.
- The rediscovery-comparison computation (§2.7, amendment) —
  `context-evaluator`'s own independent read of both agents' file lists,
  not either agent's own self-assessment.
- `reference-project-tester` friction filing via the existing
  `context-gaps`/`context-observations` queues.
- A written evaluation report under
  `planning/reference-projects/ledgerkit/` (mirroring
  `02-depth-behavioural-reconstruction-evaluation.md`'s own shape — this
  becomes `03-...`) — its own "Setup" section quotes the recorded commit
  hashes and confirms the symmetry protocol actually held (§2.1a), and
  its own verdict section carries the two-part-plus-overall structure
  (§2.6) plus the rediscovery-comparison result (§2.7).
- The explicit reconciliation of `usage.py`'s Haskell-import-detection
  deferral (§1) — a documented scope decision, not code.
- §1.5's boundary restatement (no graph-symbol integration tested here,
  `CG-008` unaffected) — carried through into the evaluation report and
  the retro, so neither can be read as claiming more than this phase
  actually tested.
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
- **General commit-pinning support for `resolve_and_clone`** — the real
  gap §2.1a found (a plain shallow clone of the upstream default
  branch's current head, no ref parameter) is worked around for this
  phase's own experiment via a manual post-sync `git checkout <sha>` in
  the affected scratch directories, not by adding ref-pinning to
  `source_resolution.py` itself. That would be a real, generalisable
  improvement (a strong learning-candidate, §"Files" below) but is a
  materially larger change (a new `EcosystemAdapter`/config surface for
  "pin to this revision") than this phase's own bounded need justifies.
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
- **Fix commit-pinning symmetry via a manual post-sync checkout in the
  experiment's own scratch directories, not via a `resolve_and_clone`
  feature (amendment)** — the smallest fix that actually closes the real
  gap §2.1a found, without expanding this phase into a general
  reproducible-cloning feature CodeCompass doesn't have today and this
  phase doesn't otherwise need.
- **Two-part-plus-overall scoring, and a required identical
  file-read-log from both agents (amendment)** — a single verdict cannot
  distinguish "helped navigation but not cross-language recognition"
  from the reverse; a treatment-only artifact log cannot support a real
  rediscovery comparison without a baseline number to compare against.
  Both additions directly serve this phase's own stated purpose
  (recognising *whether and where* CodeCompass helps, not just *that* it
  did), not scope creep beyond it.

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
- `planning/learnings/inbox.md` — any candidate learnings, at least two
  already named by this plan itself: (1) the §4 bug: "a new ecosystem
  adapter's `repository_url()` must set `subdirectory` for any monorepo
  member, or `resolve_and_clone` silently clones the wrong scope" — a
  generalisable point for *any* future adapter, not just Haskell; (2)
  the §2.1a finding: "`resolve_and_clone` has no commit-pinning support,
  so any experiment or workflow needing a fixed, reproducible vendor
  source snapshot must verify and, if needed, manually re-pin it after
  sync" — relevant to any future reproducibility-sensitive use of
  `codecompass sync`, not specific to this phase's own experiment.
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
- **Symmetry protocol actually held, checked directly (amendment,
  §2.1a)**: the recorded commit hashes match what both agents' own
  checkouts were really at (`git rev-parse HEAD` output for the
  baseline's local checkouts, the treatment's post-checkout vendor
  clones, and the scratch Ledgerkit copy — all quoted in the evaluation
  report, not merely asserted equal); both agents received the identical
  task string; neither had tool access the other lacked.
- **Both agents' own required file-read logs exist and are usable
  (amendment, §2.7)** — not merely present, but specific enough
  (per-file, with a stated reason) for `context-evaluator` to actually
  compute the rediscovery comparison from them, not reconstruct it by
  re-reading each agent's own narrative prose.
- A real `codecompass sync --yes --budget 0` against the scratch
  Ledgerkit copy succeeds for both vendors, producing real,
  independently-inspected `CLAUDE.md`/`DEPTREE.md`/`FILETREE.md` content
  for each (not just "sync exited zero").
- `depends_on_edges` (or a direct `context-graph.db` query) shows a real
  `hledger → hledger-lib` edge once both are synced and the graph is
  rebuilt — confirming the "no new code needed for cross-vendor
  relationships" claim in §1 rather than merely asserting it.
- **`context-evaluator`'s independent report carries all three verdict
  blocks (amendment, §2.6)** — Part 1 (hledger-only reconstruction,
  rated against Phase 54b's own real LOW baseline), Part 2
  (cross-language equivalence recognition, its own independent rating),
  and Overall, including the required one-sentence naming of which of
  the four outcome shapes (§2.6) actually occurred. A LOW or null result
  on either part is treated as valid evidence, not a phase failure,
  matching every prior phase's own posture.
- **The rediscovery-comparison result (amendment, §2.7) is stated as one
  of the three named outcomes** (reduced rediscovery / no measurable
  reduction / increased overhead), computed by `context-evaluator` from
  both agents' own file-read logs, not inferred from the verdict alone.
- **The evaluation report and the retro both restate §1.5's own
  boundary explicitly** — neither reads (or could be misread) as a claim
  about graph-level Haskell symbol integration, which this phase does
  not test.
- `release-phase-auditor` PASS or PASS WITH NON-BLOCKING OBSERVATIONS.

## Done when

Standard DoD (`CLAUDE.md` §5) + the `repository_url()` fix is real,
tested, and independently confirmed to produce a correctly-scoped real
clone (not merely a passing unit test) + the symmetry protocol (§2.1a)
actually held, verified via real `git rev-parse HEAD` equality, not
merely designed + both fresh-agent dispatches completed, each with its
own required file-read log (§2.7) + independently evaluated with all
three verdict blocks (§2.6: Part 1, Part 2, Overall) + the evaluation
report explicitly answers the questions this phase exists to answer:
(1) how does real Haskell-side structural information compare to Phase
54b's document-ingestion layer for the *same* `depth:` question
(Part 1's own LOW/MODERATE/HIGH, against Phase 54b's own real LOW), (2)
did CodeCompass help the treatment agent recognise hledger's and
Ledgerkit's `depth:` handling as the same behavioural concept realised
in two languages, or not (Part 2's own independent rating), and (3)
which of the four outcome shapes (§2.6) actually occurred — in
particular, whether this phase produced the specific "helped navigation,
not cross-language recognition" shape this amendment exists to make
legible, distinct from "helped both" + the rediscovery-comparison result
(§2.7) stated as one of its three named outcomes + any real friction
filed and triaged + retro states plainly (a) whether tracking a second,
differently-licensed-ecosystem vendor as ordinary CodeCompass content
(digests, source clones, dependency edges) held up at real use, not just
at the single-vendor scale Phase 60 exercised, and (b) restates §1.5's
own boundary explicitly (this phase tested adapter-derived context,
dependency structure, and vendor-source grounding — not graph-level
Haskell symbol integration, which stays `CG-008`/Phase 62's own open
question).

**Not done merely because both agents produced a plausible-sounding
answer, and not done merely because an overall verdict exists without
its own Part 1/Part 2 breakdown** — done only once `context-evaluator`'s
independent, ground-truth-verified rating exists for both parts
separately, the rediscovery comparison is computed (not asserted), and
the LOW/MODERATE/HIGH comparison against Phase 54b's own baseline is
stated honestly for Part 1, including if the result is another LOW or a
null result on either part.

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
6. **(Amendment) Fixing commit-pinning symmetry via a manual post-sync
   `git checkout <sha>` in the experiment's own scratch directories**,
   rather than adding real ref-pinning support to
   `source_resolution.resolve_and_clone` — a direct instruction's own
   requirement (exact symmetry) implemented via the smallest mechanism
   that satisfies it, not the more general fix; flagged since the more
   general fix is a real, plausible future improvement (§"Files") this
   plan deliberately does not build now.
7. **(Amendment) One combined task text asking for a per-file read log
   from both agents (§2.2, §2.7)**, rather than inferring "which files
   were consulted" from each agent's own free-form narrative after the
   fact — a methodology choice that makes both agents' own tasks
   slightly more constrained (an explicit reporting requirement neither
   Phase 54 nor Phase 54b's own tasks carried) in exchange for a
   genuinely computable rediscovery comparison; flagged since it's a new
   demand on the agents under test, not a passive observation step.
8. **(Amendment) Three verdict blocks (Part 1/Part 2/Overall) rather
   than one** — directly responsive to the instruction's own ask, not
   independently invented; flagged only because it changes what
   "PASS"/"LOW" etc. mean in this phase's own report relative to every
   prior phase's single-verdict reports, which a reader comparing across
   phases should know.
