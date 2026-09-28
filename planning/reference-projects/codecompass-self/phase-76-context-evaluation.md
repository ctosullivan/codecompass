<!-- Structure per planning/v1-redefinition/context-quality-evaluation.md §2.
     Self-hosted evaluation per planning/phase-76-git-repository-topology.md
     §15 (third amendment). -->

# Context-quality evaluation — Phase 76 Git topology (`codecompass query topology`)

## Disclosed limitation of this review (read first)

This evaluator was dispatched as a **fresh session with no visibility into
the conversation that dispatched the two agents** (`a41e247a82c745514`
baseline, `a5f0b0024e4d0e534` treatment) or their reports. Per the task's
own disclosed risk (`L-063`), I did **not** assume access to that history
and could not read either agent's transcript, raw tool-call log, or
self-reported command count. Everything below is re-derived **directly
from the fixtures, the equivalence-check file, and CodeCompass's own
source**, never from either agent's claims. Concretely this means:

- I **can** and did fully evaluate CodeCompass's own output (`query
  topology`/`--json`) for accuracy, relevance, completeness, freshness,
  grounding, noise, and trustworthiness against independently-derived
  ground truth — this is the core of a context-quality evaluation and is
  covered completely below.
- I **cannot** independently confirm what either dispatched agent
  actually did, said, or how many commands each one issued (the `L-027`
  agent-diligence-variance check and the plan's "efficiency indicator"
  command count strictly require their tool-call logs, which I do not
  have). Where the task asked me to check these, I instead (a) confirm
  the fixture-equivalence file's own symmetry claims by direct
  re-inspection, and (b) construct an objective, ground-truth-based
  minimum-command estimate for each task/arm from first principles,
  clearly labelled as such, not attributed to either agent's actual
  transcript.
- The lead should re-run this check with the two transcripts attached if
  a transcript-grounded `L-027` verdict is still required.

## Setup

- **Reference project:** CodeCompass's own repository (self-hosted
  evaluation, not an external reference project), per
  `reference-project-protocol.md`'s working-copy discipline applied to
  disposable scratch clones.
- **Pinned commit (seed):** `46ab3c573b759124445208d2c5726b00ec55c987`
  (`46ab3c5`) — independently confirmed as the `HEAD` of all four
  fixtures (`baseline-clone`, `baseline-clone-feature`,
  `treatment-clone`, `treatment-clone-feature`).
- **CodeCompass revision:** working tree at `46ab3c5` (Phase 76, "Git
  repository topology awareness"); binary invoked at
  `/home/cormac/projects/codecompass/.venv/bin/codecompass`.
- **Task:**
  - **Task A (submodule):** what commit does the parent pin for
    `adapters/haskell`; what commit is actually checked out; do they
    differ; if so, is the difference committed parent state or only
    local uncommitted child-checkout state.
  - **Task B (worktree):** are `<clone>` and `<clone>-feature` separate
    repositories or worktrees of the same repository, with what
    evidence; current checkout's branch/HEAD/dirty state; sibling's own
    branch/HEAD; which facts are live vs. persisted-from-a-prior-sync;
    whether any facility already tracks this.
- **Context CodeCompass supplied** (captured verbatim, re-run by this
  evaluator directly against `treatment-clone`/`treatment-clone-feature`,
  not taken from either agent's report):

  `codecompass query topology --help` (excerpt):
  > Git repository topology (worktrees, submodules) as of the last
  > `sync` — never invokes `git` itself, on any code path (Phase 76).

  `codecompass query topology` (plain, run in `treatment-clone`):
  ```
  Repository: .../treatment-clone/.git
  Origin: .../seed

  Active checkout: .../treatment-clone
    branch: main
    HEAD: 46ab3c573b759124445208d2c5726b00ec55c987
    workspace: dirty

  Other worktree: .../treatment-clone-feature
    branch: codecompass-phase76-eval-feature
    HEAD: 46ab3c573b759124445208d2c5726b00ec55c987
    workspace: not probed

  Submodules:
    adapters/haskell
      repository: git@github.com:ctosullivan/codecompass-adaptor-haskell.git
      parent-pinned revision: dfd7a783667a91ba5a55a9f2b534cc0c1eb746ae
      checked out: 475bfe52e5bf78725377bc3fe2557b50fa74027e (differs from pin)
      workspace: clean
    protocol/codecompass-adaptor-protocol
      repository: git@github.com:ctosullivan/codecompass-adaptor-protocol.git
      parent-pinned revision: 596fb94fae9972739f016968dee320160a803175
      checked out: 596fb94fae9972739f016968dee320160a803175 (matches pin)
      workspace: clean
  ```

  `codecompass query topology --json` (run in `treatment-clone`,
  abbreviated): `pinned_commit: dfd7a78...`,
  `checked_out_commit: 475bfe5...`, `revision_matches_pin: false` for
  `adapters/haskell`; two `worktrees` entries, current `is_dirty: true`,
  sibling `is_dirty: null`.

  `codecompass query topology --json` run in `treatment-clone-feature`
  additionally shows, for **both** submodules from that worktree's own
  perspective: `is_initialized: false, checked_out_commit: null,
  revision_matches_pin: null` — see Accuracy below, this is correct, not
  a bug.

## Independent ground-truth re-derivation (by this evaluator, both fixtures)

All confirmed directly, not taken from the equivalence-check file's word
alone — the equivalence-check file's own claims were spot-checked and all
matched:

| Fact | Ground truth (independently verified) |
|---|---|
| Parent-pinned `adapters/haskell` SHA (`git ls-tree HEAD`) | `dfd7a783667a91ba5a55a9f2b534cc0c1eb746ae` — identical in `baseline-clone` and `treatment-clone` |
| Checked-out submodule SHA | `475bfe52e5bf78725377bc3fe2557b50fa74027e` — identical in both |
| `git diff --cached -- adapters/haskell` (index vs HEAD) | **empty** in both — the index still records the committed pin (`dfd7a78`); nothing is staged |
| `git diff -- adapters/haskell` (working tree vs index) | shows `dfd7a78 → 475bfe5` in both |
| `git status` classification | "Changes not staged for commit: modified: adapters/haskell (new commits)" in both |
| → **Task A's answer** | The mismatch is **purely local, uncommitted child-checkout state** (an unstaged `git submodule update`/manual checkout) — there is **no** committed parent-side gitlink change. Confirmed independently, matches the scenario the fixture was built to represent. |
| `.git` file contents | `<clone>` is a real repo (`.git/` directory); `<clone>-feature` is a worktree (`.git` file → `gitdir: <clone>/.git/worktrees/<clone>-feature`) — identical structure in both arms |
| `git worktree list --porcelain` | 2 worktrees, `main`@`46ab3c5` and `codecompass-phase76-eval-feature`@`46ab3c5` — identical in both arms |
| Main worktree dirtiness | solely the `adapters/haskell` gitlink mismatch — no other file is dirty (confirmed via `git status --porcelain=2`) |
| Feature worktree dirtiness | solely the one-line `README.md` append (`+eval scenario edit`) — confirmed via `git diff` |
| **New finding, not in the equivalence file:** submodule initialization in the feature worktree | `git submodule status` in `<clone>-feature` shows **both submodules with a leading `-`** (not initialized) and the directories are empty — `git worktree add` does not initialize submodules by default. `codecompass query topology --json` run from `treatment-clone-feature` correctly reports `is_initialized: false, checked_out_commit: null` for both, rather than fabricating a value. This is accurate, non-obvious Git behaviour that could otherwise look like an inconsistency between the two worktrees' topology reports. |
| **New finding, empirically tested by this evaluator, not present in either fixture's actual outcome:** cross-worktree staleness of sibling branch/HEAD | In a disposable scratch repo (not the evaluated fixtures), I synced worktree A, then advanced worktree B's HEAD with a new commit, then re-queried topology from A **without re-syncing A**. A still reported B's **old, pre-advance HEAD** — confirmed the tool never re-probes a sibling at query time, exactly as `docs/cli-reference.md` states ("every other known worktree, with its own branch/HEAD as observed at the current checkout's own last sync — never live"). This did **not** cause a wrong answer in the actual Phase 76 fixtures (nothing changed between either worktree's own sync and this evaluation), but it is a real, latent, documented-only-in-prose limitation — see Material gaps. |
| `revision_matches_pin` field / schema | Confirmed by reading `git_topology.py::_detect_pinned_commit` (uses only `git ls-tree HEAD`, never the index separately) and `graph.py`'s `git_submodules` table DDL (no staged/index-state column) — there is genuinely **no field** capturing "is the pin itself staged-but-uncommitted," distinct from "is the checkout locally diverged." Both arms needed ordinary `git diff --cached`/`git status` for this. |
| Sync-timestamp field | Confirmed absent from `git_repositories`, `git_worktrees`, `git_submodules` DDL (`graph.py` lines 211-247) — no column records *when* a row was last written. The only way to detect asymmetric sync times between the two treatment worktrees is external: `context-graph.db` file mtimes (`treatment-clone`: 14:55:56; `treatment-clone-feature`: 14:58:11 — independently confirmed via `stat`). |
| `--help`'s "never invokes `git`" claim | Verified true by reading `cli.py::query_topology` and `graph.py::topology_profile` — both are pure SQL reads of `context-graph.db`; no `subprocess`/git call anywhere in the query path (as opposed to `sync`, which does shell to `git`). |

## Criteria assessment

| Criterion | Rating | Notes |
|---|---|---|
| Accuracy | **strong** | Every claim in both plain and `--json` output — repository identity, both worktrees' branch/HEAD/dirty, both submodules' pin/checkout/match verdict, and the non-obvious `is_initialized: false` state in the feature worktree — matched independently-derived ground truth exactly, in both fixtures. No fabricated or incorrect claim found anywhere I checked, including the "never invokes git" disclosure (verified against source). |
| Relevance | **strong** | The two questions asked are precisely what `query topology` was built to answer; nothing generic or off-task in the output. |
| Completeness | **adequate** | Covers the core mechanical facts for both tasks fully and correctly, but by design/gap it does **not** answer: (1) Task A's own explicit second half — committed-vs-uncommitted nature of the pin/checkout mismatch (no field for it); (2) the actual dirty-content diff (correctly out of scope for a topology command); (3) at the *output* level, it does not flag that a sibling's reported branch/HEAD (not just its dirty flag) can be stale relative to sync time — that caveat exists only in `docs/cli-reference.md` prose, not in the CLI/JSON output itself. Ordinary `git` was still required for (1) in both arms. |
| Freshness | **adequate** | Data reflected the pinned seed commit and each worktree's own last-sync state accurately in these specific fixtures (nothing drifted between sync and my inspection). The demonstrated cross-worktree staleness risk (see Material gaps) is a structural property of the design, not triggered here, but real and worth flagging as "adequate" rather than "strong." |
| Grounding / provenance | **adequate** | Every field is traceable to a specific, named source via source-code inspection (`git ls-tree HEAD`, `git worktree list`, `git submodule`-equivalent plumbing in `git_topology.py`), and `docs/cli-reference.md`'s topology section is accurate against source, including the "never live" sibling caveat. Rated adequate rather than strong only because I could not verify the two dispatched agents' *own* grounding of their claims (no transcript access — see disclosed limitation above); CodeCompass's own output grounding is itself strong. |
| Noise | **strong** | Compact, single-purpose; every field maps directly onto Task A/B's questions. |
| Safety / trustworthiness | **strong** (with one caveat) | Consistent, correct honest-abstention throughout: `is_dirty: null` / "not probed" for the unprobed sibling, `is_initialized: false` / `checked_out_commit: null` rather than fabricating a value for a genuinely uninitialized submodule, and a verified-true "never invokes git" claim. The one blemish: a sibling's branch/HEAD is presented with the same confident formatting as the current checkout's own live data, with no inline signal that it is a last-sync snapshot rather than a live read — unlike the dirty flag, which is explicitly nulled. This did not produce a wrong answer in this evaluation but is a real gap between what the output implies and what only the docs disclose. |

## Verdict: PASS WITH GAPS

No incorrect or misleading claim was found anywhere in CodeCompass's
`query topology` output, in either fixture, against independently
re-derived ground truth — including a genuinely non-obvious edge case
(submodules uninitialized in a worktree added via `git worktree add`)
that the tool represented correctly rather than papering over. That rules
out FAIL under this spec's own §4 (incorrect/misleading content
outranks incompleteness). However, real, material context was absent
from the tool's direct output and required supplementary ordinary `git`
work or prior documentation-reading in both arms: the committed-vs-
uncommitted distinction for the submodule mismatch (Task A's own explicit
second half), and the fact that a sibling worktree's reported branch/HEAD
— not just its dirty flag — can silently go stale relative to sync time,
disclosed only in prose docs, not at the point of output. Trustworthy,
not fully sufficient standing alone — the textbook PASS WITH GAPS case.

## Context advantage: MODERATE

**Could a competent fresh Claude session have obtained equivalent context
trivially?** Partly. `git worktree list --porcelain`, `git submodule
status`, and `git status`/`git diff --cached` are ordinary, discoverable
commands — a diligent baseline agent would reach the same correct answers
with git alone, and ground truth here needed nothing exotic. That keeps
this off HIGH. But it is not LOW either: `git submodule status`'s
`+`/`-`/`(blank)` prefix convention is a genuinely easy-to-misread
plumbing detail (this evaluator had to re-verify it directly rather than
trust memory), a rigorous "committed vs. uncommitted" submodule verdict
needs 2-3 separately-interpreted commands combined correctly, and
`codecompass query topology`'s single call answers the repository-identity
and pin/checkout match-or-mismatch questions for **both** submodules and
**both** worktrees at once, compactly and with explicit non-fabrication
(`null`/"not probed") where it genuinely doesn't know something — a
diligent-but-less-careful agent could plausibly get the raw `git`
plumbing right but phrase the "do we know the sibling is dirty?" question
less honestly than CodeCompass's own explicit null does. This matches the
spec's own MODERATE definition precisely: "meaningfully shortened the
path... but a diligent agent would have gotten there."

**Ground-truth-based command-count estimate** (not derived from either
agent's actual transcript — see disclosed limitation):
- Task A, minimum ordinary-git commands to fully answer (SHAs + mismatch
  + committed-vs-uncommitted): ~2 (`git submodule status` combined with
  `git ls-tree HEAD -- adapters/haskell`, plus `git status`/`git diff
  --cached` for the committed-vs-uncommitted half).
- Task A via CodeCompass: 1 (`query topology --json`, gives both SHAs and
  the match verdict) + the same ~1 supplementary `git status`/`git diff
  --cached` call neither arm can skip, since the tool has no field for
  it. Net saving: the SHA/mismatch determination, not the
  committed-vs-uncommitted determination.
- Task B, minimum ordinary-git commands (repo-identity + both worktrees'
  branch/HEAD + current's dirty state): ~2 (`git worktree list
  --porcelain` gets identity + both branches/HEADs in one call; `git
  status` for current's own dirty state). Sibling's dirty state is not
  obtainable without a third command visiting it directly, or explicitly
  reported as unknown.
- Task B via CodeCompass: 1 call gets all of the above **plus** an
  explicit, correctly-labelled `null` for the sibling's dirty state
  (rather than requiring the agent to reason about why it can't be
  determined without visiting it). Net saving here is real and slightly
  larger than Task A's — a genuine ~2-call-to-1-call reduction with an
  honesty guarantee attached, not just a formatting convenience.

## Material gaps / failures

- **Gap 1 — no field distinguishes a staged-but-uncommitted parent
  gitlink bump from purely local, unstaged child-checkout drift.**
  `git_submodules.pinned_commit` is sourced only from `git ls-tree HEAD`
  (confirmed in `git_topology.py::_detect_pinned_commit`); the schema
  has no column reflecting the *index's* own gitlink SHA. Task A's own
  explicit second question ("committed parent state, or merely local
  child-checkout state?") is exactly this distinction, and CodeCompass's
  own JSON cannot answer it — both arms needed ordinary `git status`/
  `git diff --cached` regardless of CodeCompass's availability.
- **Gap 2 — a sibling worktree's reported branch/HEAD can be stale
  relative to sync time, with no inline signal distinguishing it from the
  current checkout's own live-equivalent data.** Empirically confirmed
  (see table above, disposable scratch repo, not the evaluated fixtures):
  advancing a sibling's HEAD after the querying checkout's own last sync
  leaves the querying checkout reporting the sibling's **old** HEAD,
  indefinitely, until the querying checkout itself re-syncs (re-syncing
  the sibling does not fix this from the other side — each worktree owns
  a wholly separate `context-graph.db`). This is disclosed in
  `docs/cli-reference.md` prose ("never live") but **not** in the CLI/
  JSON output itself — the sibling's dirty flag is explicitly nulled,
  but its branch/HEAD fields carry no equivalent "as of last sync of
  <this checkout>" marker, so they read with the same confidence as
  live data unless the reader has already read the docs. Did not cause
  a wrong answer in the actual Phase 76 fixtures (nothing changed
  between either worktree's own sync and this evaluation), but is a
  real, latent risk directly relevant to Task B's own explicit
  "which facts are live vs. persisted" question.
- **Gap 3 (assessed, not filed) — no automatic dirty-state for
  siblings.** Confirmed intentional, by design, and already correctly,
  explicitly disclosed as `null`/"not probed" in both the JSON and the
  plain rendering (`git_topology.py`'s own docstring: "probing a
  sibling's workspace would require an extra filesystem walk this
  command chooses not to perform"). This is honest abstention, not a
  misrepresentation — I do not think it independently warrants a new
  context-gap entry beyond what Gap 2 above already covers for the
  worktree side.
- **L-027/L-062 symmetry check:** confirmed, from the fixtures and the
  equivalence-check file alone (re-verified independently, not taken on
  its word — every row in its comparison table was independently
  reproduced and matched), that both arms had identical, scoped Git
  access to an identical scenario; the only designed difference is
  CodeCompass's own availability/sync state. I could **not** verify from
  here whether either dispatched agent's *actual* tool-call log stayed
  within that scope or whether the treatment agent's report reveals any
  read a baseline agent structurally could not have made — that requires
  the two transcripts, which were not available to this session. This
  should be re-checked by whoever holds those transcripts before any
  specific finding is credited to CodeCompass rather than agent
  diligence.

### Candidate context-gap entries (drafted, not filed — see note)

Checked against `CG-001` through `CG-009`: none touch Git topology,
worktrees, or submodules at all (all predate Phase 76 and concern
doc/symbol/dependency-graph relationships). Both candidates below are
therefore first occurrences, not duplicates. Per this role's own write
boundary ("write only your report file... never edit CodeCompass docs"),
I have **not** written these to `planning/context-gaps/inbox.md` myself;
I recommend the lead or `knowledge-curator` file them as `CG-010`/`CG-011`
using the material above (Gap 1 and Gap 2) and the template's exact
fields, classified as follows:

- **Gap 1** (submodule committed-vs-uncommitted): `edge kind: other`
  (matches the `CG-008`/`CG-009` precedent for architecture/ingestion-
  scope gaps); `could mechanical detection ever catch this?
  yes-with-better-heuristics` — compare the index's own gitlink SHA
  (`git ls-files --stage -- <path>`, already available without
  contradicting "query never invokes git," since `sync` already shells
  to `git`) against `HEAD`'s; `classification: detection-improvement`
  (a small, additive `git_submodules` column populated by a git call
  `sync` already makes elsewhere, not a new ontological concept).
- **Gap 2** (sibling staleness, no inline signal): `edge kind: other`;
  `could mechanical detection ever catch this? yes-with-better-
  heuristics` — a per-worktree `synced_at` column (or reusing the
  existing per-row sync generation, if one exists elsewhere in the
  schema) surfaced in `query topology --json`'s sibling entries, the
  same class of fix the task description's own "no sync-timestamp field"
  observation already points at; `classification: graph-capability`
  (needs a new schema column plus a rendering decision about how to
  present relative staleness, closer to `CG-008`/`CG-009`'s own scope).

## Would this have misled the implementing agent? no

Expansion: in the two Phase 76 fixtures as actually constructed, nothing
CodeCompass reported was wrong, and every place it did not know something
it said so explicitly (`null`/"not probed") rather than guessing — so, as
delivered, this would not have misled either agent. The qualifier is
Gap 2: the general mechanism that would let a stale sibling HEAD read as
live was not exercised by this static fixture (both worktrees' syncs
happened within ~2 minutes of each other with no further commits), but I
confirmed it exists and is real via a separate, controlled experiment. A
follow-up fixture that advances a sibling's HEAD *after* the current
checkout's own sync, then re-asks Task B, would be a good, cheap way to
turn this from a latent to a directly-observed risk in a future
iteration of this same self-hosted evaluation.
