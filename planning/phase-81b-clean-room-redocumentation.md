# Phase 81B — Clean-room project redocumentation from intermediary knowledge

**Status: planned.** Not started, not in progress. Direct user request,
2026-10-08. **Implementation is explicitly gated on direct user approval
of this committed plan.** No clean-room branch, isolated workspace,
writer dispatch, documentation deletion, or `codecompass-template`
change may happen until that approval is given. Phase 81 (persistent
bidirectional intermediate knowledge layer, all three corrective passes)
remains `done`, unmodified, not reopened by this phase. Phase 81B is a
distinct, later, additive phase — it *consumes* Phase 81's own
deliverable (the intermediary-knowledge render/reconcile loop) as an
input capability; it does not alter Phase 81's own history or code.

**Amendment note (2026-10-08, same day, before implementation began)**:
ten corrections were made on review, in place, following this project's
own established convention (see `planning/phase-81-intermediate-knowledge-layer.md`'s
own amendment notes) of revising a still-unapproved plan directly rather
than appending a contradicting note, with the correction itself recorded
here so a reader never needs git history to understand why the design
looks the way it does. Summary: (1) **verified Mode B isolation is now a
hard prerequisite** for the authoritative clean-room run — a
`best-effort`/`UNMET` outcome blocks Phase 81B rather than satisfying it
(§6.3, §18, §21); (2) **no pre-existing human-facing narrative
documentation may reach the writer**, including `docs/domain/**` and
anything copied from the current `README.md` — old prose is a
preparation-side input only, never writer-visible, and must pass through
validated knowledge before it can influence the handoff (§1.2, §7, §9.1,
§12.1); (3) the clean-room branch now carries an **explicit, named
allowlist/exclusion list**, not an ambiguously-described "handoff
filesystem" (§6.1.1); (4) the **cold-reader gate now runs inside the same
verified Mode B boundary as the real writer** — a Mode A cold-reader pass
is no longer treated as evidence the handoff is sufficient (§13); and the
template, render/include, "full re-doc," and preparation/writer
trust-boundary points below. Every section this touches is marked
inline; nothing is silently rewritten without a trace, consistent with
§24's own stated preference, now extended by a dedicated plan-review
pass against seven named invariants (§24).

## 0. What this document is, and what it is not

This is a **planning artefact only**, produced by investigating the
current state of both `ctosullivan/codecompass` and
`ctosullivan/codecompass-template` (§1 below records exactly what was
found, with real numbers — not assumed). It commits to an
implementation-ready design. It does **not** itself create a branch,
export anything, dispatch a writer, or touch either repository's
documentation. Per `CLAUDE.md` §1, the plan exists before the code; this
phase's own code does not exist yet.

---

## 1. Investigation findings (grounding this plan in reality, not assumption)

### 1.1 CodeCompass's intermediary-knowledge coverage is real but shallow and concentrated

Only two of five `planning/knowledge/<slug>/` directories have ever been
rendered through `codecompass knowledge render` at all
(`codecompass-domain`, the project-wide slug, and `hledger-depth`, a
Ledgerkit-relevant phase slug). The other three
(`doc-origin-pinned-reference`, `first-party-source-symbols`,
`haskell-api-surface-extraction`) are Phase 54c context-packet-research
slugs with real canonical records but no `intermediate/` projection at
all — they describe specific CodeCompass capabilities (first-party
source indexing, Haskell API extraction, doc-origin pinning) and are
genuinely relevant project knowledge, currently invisible to the
rendering pipeline.

Within `codecompass-domain`'s own rendered projection, the concentration
the governing request anticipated is real and measured, not assumed:

```
  9 lines  interfaces-and-behaviours.md
  9 lines  invariants-and-constraints.md
  9 lines  open-questions-and-conflicts.md
321 lines  overview.md
 18 lines  phase-brief.md
```

321 of 366 total lines (88%) sit in `overview.md`. The three structural
files are each only the boilerplate header with zero real content. The
cause is confirmed directly in the record data, not inferred: of 31
`claim` records in `codecompass-domain`, **exactly one** has an
`assertion_kind` field set at all (`definition`); the other 30 have none.
`_file_for_record`'s dispatch (`src/codecompass/knowledge_intermediate.py`)
routes any Claim with no `assertion_kind` to `overview.md` by default —
not a rendering bug, a direct, mechanical consequence of the underlying
records never having been classified. Zero `decision` or `requirement`
records exist in `codecompass-domain` at all. **This is the
"intermediary export" problem §1.2.1 is built to fix**: successful
rendering (every record resolves to a file, no crash) has been
conflated with adequate coverage (records classified so they land in the
*right* file). They are not the same thing, and this plan does not
repeat that conflation.

### 1.2 Existing current-truth documentation, with real sizes

| Area | Size | Notes |
|---|---|---|
| `README.md` | 370 lines | product-facing, includes a real `codecompass-grounded-by` region (Phase 81) |
| `architecture/overview.md` | 1,186 lines | already once reduced by Phase 64's blank-slate reconstruction (was 1,954 lines per `planning/v1-redefinition/documentation-lifecycle.md` §1.1's own cited figure) — still large |
| `architecture/{adapter-interface,context-graph-schema,core-data-model,historical-notes,module-map,sync-and-enrichment-pipeline}.md` | ~1,290 lines combined | `historical-notes.md` (106 lines) is **already** an explicitly historical page, kept inline in the normal `architecture/` navigation — a different convention from what this plan proposes (§6) |
| `docs/domain/` (19 concept pages + glossary/examples/etc.) | ~3,125 lines | Phase 63D/79/80's own evidence-backed domain corpus — **revised by amendment 2 (§7.1)**: its *semantic content* (what CodeCompass's concepts mean) remains valuable preparation-side input, but as **narrative prose** it is human-facing documentation like any other and receives the same explicit disposition as everything else — the writer never sees these files themselves, only whatever of their content survives re-grounding into validated knowledge |
| `docs/` (cli-reference, config-schema, knowledge-workflow, quickstart, developer/, protocol-adapter/) | substantial, actively maintained | user/developer/protocol documentation categories per `documentation-lifecycle.md` §1.4 |
| `ai-docs/` | 2 files | agent-orientation pointer docs |

### 1.3 Prior clean-room isolation work exists and already reached a firm, honest conclusion — this plan must not re-derive or contradict it

Phase 79 (`decisions/0066`) and Phase 80 both ran the clean-room
methodology (frozen snapshot → model-blind implementation reconstruction
→ comparison → fresh draft → legacy reconciliation) and both **honestly
report strict clean-room isolation as `UNMET`**, for a documented reason
that does not depend on which dispatch or which topic: every isolation
attempt used either a same-host curated export directory (content the
dispatch was *pointed at*, never prevented from reaching anything else)
or instruction-only scoping (full tool access, told what to stick to).
A real preflight probe (`planning/knowledge/first-party-source-symbols/isolation/tier1-preflight.md`)
found `Agent(isolation: "remote")` behaved as a same-host git worktree in
this environment, failing all five required routes (filesystem, search,
command, network, delegation). A corrected evidence inventory
(`.../isolation-evidence-inventory.md`) found one real dispatch
(`knowledge-curator`'s packet assembly) actually crossed its own
instructed boundary (two out-of-scope reads, caught only by a mechanical
transcript check, not by the dispatch's own self-report).

A backlog item already exists recording exactly this gap and proposing
to fund closing it:
[`planning/strict-isolation-for-documentation-reconstruction.md`](strict-isolation-for-documentation-reconstruction.md)
(`planning/ROADMAP.md`, Priority D cross-reference, "candidate, not
funded, not scheduled"). **Its own stated revisit trigger is: "a third
independent application of the clean-room methodology reconfirms the
same gap a third time... OR a genuinely separate execution substrate
becomes available/confirmed in this project's own working
environment."** Phase 81B **is** that third application. This plan
therefore does not re-propose the backlog item's own scope from scratch
— §6/§21 below adopt it directly, extend it with one new, concrete,
not-yet-verified candidate mechanism (§1.4), and commit Phase 81B's own
implementation to resolving that backlog item's trigger one way or the
other, honestly, rather than leaving it open a fourth time.

### 1.4 A candidate genuinely-separate execution substrate was found during this planning investigation — not yet proven, explicitly not claimed as working

Unlike `Agent(isolation: "remote")` (tested at Phase 79, found to behave
as same-host), this environment has `unshare`/`nsenter` (Linux namespace
tools) available, and unprivileged user namespaces are usable here. Two
narrow, read-only probes run during this planning investigation (no
clean-room artefact created, nothing of Phase 81B's own scope touched):

```
$ unshare --net --map-root-user echo "ok"          → succeeded
$ unshare --net --map-root-user -- curl -m3 https://github.com
  → curl exit 6 (could not resolve host), HTTP_CODE 000
```

A network namespace with no interfaces configured genuinely blocks
outbound connectivity, including DNS — a stronger result than anything
tried at Phase 79/80, where the identified leak was specifically
*network egress through a granted `Bash` bypassing filesystem isolation*
(`decisions/0066`'s own finding). Combined with a mount namespace
restricting the visible filesystem to only the exported clean-room tree,
this is a genuine candidate for a mechanically-enforced Mode B boundary
(§6).

**This is not a confirmed capability.** It is a lead to test, during
Phase 81B's own implementation, against the full five-route-preflight-
plus-active-escape protocol (§21) — not something this plan is entitled
to assume will work end to end. One specific, real, currently-unsolved
sub-problem must be resolved before it can be trusted: **if the writer
itself is an AI agent, it needs some network path back to its own model
provider to function at all** — "no network" and "no agent" are the
same outcome unless the mechanism can distinguish "reach the model
API" from "reach `github.com`/any other destination." §6.3 names three
candidate resolutions (scoped egress allowlist; a fully local/offline
writer; a human-in-the-sandbox writer) as an explicit open question for
implementation to resolve and report on, not pre-decide here.

### 1.5 Reusable project capabilities this plan builds on, rather than reinventing

- **Agents**: `docs-reconstructor` (MILESTONE mode already does a
  from-reality, ignore-old-structure reconstruction — Phase 64 — but with
  *no* mechanical isolation, an important distinction from Phase 81B,
  §1.6); `implementation-reconstructor` (model-blind-by-design, already
  used at Phase 79/80); `domain-skeptic` (comparison mode, already
  classifies `aligned`/`partial`/`conflicting`/`not_implemented`/
  `insufficiently_verified`); `context-researcher`; `knowledge-curator`
  (context-packet assembly); `release-phase-auditor`.
- **Scripts**: `scripts/check_knowledge_base.py` (`check_anchor_integrity`,
  `check_requirement_cites_approved_decision`, the `assertion_kind`
  closed-enum validator — confirmed values: `definition`, `relationship`,
  `rule`, `invariant`, `state_transformation`, `boundary`, `workflow`,
  `constraint`); `scripts/check_user_docs.py` (`check_internal_links_resolve`,
  `check_no_deleted_names_as_live`, `check_generated_artifacts_match_source`
  — confirmed narrow: only the `CLAUDE.md` routing table and vendor Skill
  files, **not** `knowledge_intermediate.py`'s own projections; §9 names
  this as a genuine gap this phase closes).
- **Governance**: `planning/v1-redefinition/documentation-lifecycle.md`
  §1's three-role split (current truth / decision history / historical
  milestone state) and §1.4's six content categories (domain /
  architecture / user / developer / protocol-adapter / development-
  process) — Phase 81B's own disposition classification (§7) maps onto
  this existing framework rather than inventing a parallel one.
- **`isolation-evidence-inventory.md`'s own standing rule**, now already
  project convention: *honest `best-effort` compliance is never the same
  claim as isolation being achieved.* Phase 81B inherits this rule
  unconditionally (§21).

### 1.6 Phase 81B is a qualitative upgrade over Phase 64's blank-slate reconstruction, not a repeat of it

Phase 64 (`documentation-lifecycle.md` §3) already does "approach the
project as though current narrative documentation did not exist" — but
via an *instruction* to the same `docs-reconstructor` agent, with full,
ordinary tool access and no manifest, no branch, no filesystem
isolation, and no prevention of reading old docs. It is exactly the
"instruction-only" posture Phase 79/80 already found insufficient for an
isolation claim. Phase 81B's own distinguishing contribution is making
that same "write from zero" discipline **mechanically enforced** (branch
+ manifest + isolated filesystem, Mode B) rather than merely instructed
— the real, hard-won gap this project has already spent two phases
honestly reporting as open.

### 1.7 `codecompass-template`'s current state

`optional-clean-room-workflow/mechanical-isolation.md` already ships a
portable, tool-agnostic `verified`/`best-effort` isolation-labelling
framework for downstream users (consistent with the backlog item's own
"a short pointer... once a working approach exists" commitment — no
template change happens in this planning task, and none should happen
until a working Phase 81B mechanism actually exists to point at).
`codecompass-template`'s full file tree, current sizes:
`README.md` (161 lines), `docs/architecture.md` (31), `docs/worked-example.md`
(51), `optional-clean-room-workflow/README.md` (66),
`optional-clean-room-workflow/conceptual-documentation-guide.md` (63),
plus nine clean-room workflow templates and the Phase 81
`optional-intermediate-knowledge/` directory already updated this
session. No `architecture/`, no `docs/domain/` — confirming the
governing request's own expectation that the template's redoc should be
intentionally lighter (§11).

---

## 2. Phase purpose (restated, grounded)

Operationalise the capabilities Phases 79, 80, and 81 already built
(frozen knowledge snapshots, model-blind implementation reconstruction,
informed comparison, and now a persistent, reconcilable intermediary-
knowledge layer) into a **reproducible, whole-project clean-room
documentation reconstruction workflow**, run to completion on both
`ctosullivan/codecompass` and `ctosullivan/codecompass-template`, ending
with each repository fully, currently, and cleanly redocumented — no
old and new documentation competing side by side.

The phase is not complete merely because the mechanism works (§17). It
is complete only once both repositories have actually been
redocumented using it, superseded documentation has an explicit,
executed disposition, and the proven workflow is durably stored in the
repository for a future maintainer or agent to repeat without any
knowledge of this conversation.

## 3. Explicit non-goals for Phase 81B (carried from Phase 81's own discipline)

No MCP. No new UI. No broad ontology/schema change to the six-record
knowledge model. No autonomous semantic/product decisions made by any
agent on the user's behalf. No reopening of Phase 78 (Priority A) or any
of Priorities A/B/C/E/F. No change to `codecompass-template` until a
working mechanism exists to document there. No claim of `verified`
isolation that the implementation did not actually demonstrate.

**Amended by the second revision (§6.3/§18/§21): unlike Phase 79/80, a
`best-effort`/`UNMET` isolation outcome is no longer an acceptable
terminal result for Phase 81B's own authoritative clean-room run.**
Phase 79/80 correctly treated `UNMET` as honest and sufficient for their
own, narrower charters (probing isolation, not gating a production
redocumentation run on it). Phase 81B's own charter is different: its
entire value proposition is that the *authoritative* re-doc genuinely
could not have seen old documentation or the original repository. A
`best-effort` writer run does not establish that — it only establishes
good behaviour under an unenforced instruction, the exact distinction
`isolation-evidence-inventory.md` already draws. A failed isolation
attempt remains honestly recorded, real evidence, and is not wasted
work (§6.3) — it simply does not authorise proceeding to the
authoritative writer run. If no mechanism in the real environment
achieves `verified` isolation, Phase 81B is **blocked**, not `done` via
a downgraded claim (§18).

---

## 4. Architecture — the lifecycle (as specified, grounded in real tool names)

```
main @ SOURCE_REVISION
        │  Preparation (§9): reconcile pending knowledge-layer edits
        │  (codecompass knowledge select-candidates/apply, every slug),
        │  validate (scripts/check_knowledge_base.py --strict), enrich
        │  materially missing assertion_kind/decision/requirement
        │  coverage (never fabricate), re-render + drift-check EVERY
        │  knowledge slug for repository consistency (§9/§9.6) — distinct
        │  from which validated knowledge is actually SELECTED into the
        │  handoff (§9.6/§22).
        │  Old human-facing prose (README/docs/architecture/ai-docs/
        │  docs/domain/**) may be read here, by the orchestrator only, to
        │  find gaps/terminology/stale-vs-current statements — never
        │  copied forward; anything useful is re-grounded into a real
        │  Claim/Evidence pair first (§7.1, §9.1, Amendment 2).
        ↓
validated canonical knowledge (planning/knowledge/)
        ↓
complete intermediary export (rendered intermediate/*.md, all five
  CodeCompass-relevant slugs; a lighter equivalent synthesis for
  codecompass-template, which has no planning/knowledge/ of its own,
  built only from structural/product evidence, §9.5/Amendment 5)
        ↓
documentation inventory + disposition decision (§7) — classify EVERY
  existing human-facing narrative file, with no implicit exemption
  (README/architecture/ai-docs/docs/**, including docs/domain/**) BEFORE
  building the handoff, so the clean-room writer is never shown any of it
        ↓
explicit handoff selection (§9.6) — from validated, all-slugs-rendered
  knowledge, choose what's documentation-relevant; persist the selection
  criteria and the chosen ids/slugs in the manifest (Amendment 6)
        ↓
clean-room handoff filesystem, under an explicit, named allowlist
  (§6.1.1): planning/documentation-handoff/ (§8)
        ↓
durable clean-room Git branch: cleanroom/redoc-<source-revision> (§6),
  manifest records the allowlist/exclusion list verbatim
        │
        ├──────── Mode A: git diff/checkout from the ordinary repo —
        │         human review, trusted-tool handoff, debugging ONLY
        │         (§6.1) — never treated as evidence the handoff is
        │         sufficient for the real writer (Amendment 4)
        │
        ↓
history-free isolated workspace, derived via `git archive` (§6.2)
        ↓
PROVE Mode B isolation (§6.3/§21): active escape attempts against every
  named route — filesystem/history/branches/remotes/network/GitHub/
  credentials/MCP/agent-context
        │
        ├── UNMET / best-effort → Phase 81B BLOCKED (§6.3 outcome 3) →
        │     do not proceed to the cold-reader or writer stages below;
        │     investigate a different execution substrate (Amendment 1)
        │
        ↓ VERIFIED MODE B
        ↓
fresh cold-reader, dispatched INSIDE the same verified Mode B boundary
  (§13/Amendment 4) — not Mode A, not the orchestrator's own context
        │
        ├── handoff insufficient → back to preparation (§9) /
        │     handoff selection (§9.6), not forward
        │
        ↓ handoff sufficient
        ↓
fresh documentation-writing agent (tool-independent, §19), inside an
  equivalent verified Mode B boundary, writing only to /output (§6.4)
        ↓
complete new README + docs from zero, per repository (§12) — every
  pre-existing narrative artefact's own disposition executed, no
  category implicitly exempt (Amendment 7)
        ↓
result branch: cleanroom/redoc-<revision>-result (§14)
        ↓
independent, informed verification (domain-skeptic comparison mode,
  full repository/canonical access, old documentation usable only as
  comparison/history, never as authority, never relayed to the writer,
  Amendment 9) — supported/unsupported/contradicted/missing/
  insufficiently-evidenced (§15)
        ↓
superseded-documentation deletion/archival, executed (§7/§8), per the
  disposition report
        ↓
integration branch → main, link/navigation reconciled
        ↓
clean, current, fully redocumented repository
```

A second, parallel lifecycle (lighter) runs the same shape for
`codecompass-template` (§11), with its own handoff, its own branch
naming (`cleanroom/redoc-template-<source-revision>`), and its own,
much smaller documentation set.

**Central principle, unchanged from the governing request**: the
clean-room Git branch is the durable, inspectable *contract* describing
exactly what the writer was permitted to know. The branch alone is
Mode A — reviewable, portable, not isolation. Only a workspace *derived*
from the branch, run where the original repository and its history are
technically unreachable, is Mode B — the actual isolation claim.

---

## 5. Why not simply extend Phase 64's blank-slate reconstruction in place

Considered and rejected as the *only* mechanism (though its underlying
"ignore old structure" discipline is reused): instruction-only scoping is
exactly the posture Phase 79/80 already spent two phases demonstrating
is not an isolation claim. Phase 81B's own contribution has to be the
mechanical enforcement Phase 64 never attempted — reusing Phase 64's
"write from reality, not old structure" *goal*, replacing its
*mechanism*.

---

## 6. Clean-room Git branch design

### 6.1 Branch, naming, and Mode A

`cleanroom/redoc-<source-revision>` for CodeCompass (`<source-revision>`
= the short commit SHA Phase 81B's own implementation freezes against);
`cleanroom/redoc-template-<source-revision>` for `codecompass-template`.
Derived from a specific, recorded commit — never `main`'s own moving
HEAD. Contains **only** the clean-room handoff filesystem (§11) plus
three durable manifest/instruction files at its own root:

```
CLEANROOM-MANIFEST.yaml
CLEANROOM-INSTRUCTIONS.md
DOCUMENTATION-TARGET.md
```

`CLEANROOM-MANIFEST.yaml` records at minimum:

```yaml
source_repository: ctosullivan/codecompass
source_revision: <commit sha>
generated_at: <ISO 8601 timestamp>
codecompass_version: <pyproject.toml version string at source_revision>

included_paths: [...]      # the FULL, explicit allowlist (§6.1.1) --
                            # every path actually present, listed, not
                            # summarised
excluded_paths: [...]      # named exclusions (§6.1.1's own EXCLUDE list),
                            # so a reviewer sees what was deliberately
                            # left out, not just what's present

all_rendered_knowledge_slugs: [...]     # every slug re-rendered/drift-
                                         # checked for repository
                                         # consistency this cycle (§9.6)
handoff_selected_slugs: [...]           # the subset actually chosen for
                                         # this handoff, with the
                                         # selection criteria recorded in
                                         # INDEX.md (§9.6, Amendment 6) --
                                         # never "all of them, because
                                         # they exist"
intermediary_projection_hashes:     # slug -> {file: sha256}, so a reviewer can
  ...                               # confirm the handoff matches a specific,
                                    # frozen render, not a moving target

documentation_disposition: <path to the disposition report, §8.3>

network_policy: <what Mode B actually enforces, stated plainly — not aspirational>
history_policy: "none -- this filesystem has no .git directory, see §6.2"
credential_policy: "none -- no SSH keys, tokens, or env-var secrets included"
narrative_documentation_policy: "none of README.md/docs/**/architecture/**/
  ai-docs/**, including docs/domain/**, is present in this filesystem in
  its own original prose form -- see §6.1.1's own EXCLUDE list and
  Amendment 2"
```

### 6.1.1 The explicit writer-visible allowlist (Amendment 3 — replaces "handoff filesystem" as an ambiguous term)

The branch's own tree is **exactly** the union of two named sets, nothing
implied, nothing inherited by omission:

**ALLOW** (source/evidence genuinely needed to understand and verify the
current implementation):

```
src/**
tests/**
pyproject.toml
relevant package/build metadata (vendor.toml, lockfiles, etc.)
schemas/**                         -- where they exist as real, current files
protocol/interface definitions     -- where current (e.g. the real wire-
                                       protocol source, not its prose doc)
configuration fixtures
other source-like runtime assets genuinely needed for verification

planning/documentation-handoff/**  -- the handoff package itself (§8)
CLEANROOM-MANIFEST.yaml
CLEANROOM-INSTRUCTIONS.md
DOCUMENTATION-TARGET.md
```

Any path proposed for inclusion beyond this starting list must be
justified explicitly, in the manifest's own `included_paths` comment, as
source/evidence the writer needs to verify a specific technical claim —
never justified as "it was already documentation," which is precisely
the posture this amendment closes off.

**EXCLUDE** (named explicitly, not merely "everything else"):

```
README.md
docs/**                            -- including docs/domain/** (Amendment 2)
architecture/**
ai-docs/**
old generated narrative documentation / old documentation examples
.git/**
planning/retros/**                 -- raw retrospectives
planning/ROADMAP.md, planning/CONTEXT.md  -- raw phase history
architecture/historical-notes.md   -- historical narrative
decisions/**                       -- the full ADR corpus (its summarised
                                       rationale enters only via
                                       decisions-and-rationale.md, §8.2,
                                       never the originals)
```

Where decision knowledge is relevant to the writer, it is always the
prepared `decisions-and-rationale.md` synthesis (§8.2) that is allowed
in, never the raw `decisions/*.md` files themselves.

Mode A review is exactly `git diff <source-revision>...cleanroom/redoc-<source-revision>`
from the ordinary CodeCompass checkout — a maintainer sees precisely
what was added/exposed, nothing more, and can confirm by eye that the
diff contains only ALLOW-listed material. **Mode A is review/portability
only — it is never, by itself, evidence that the real writer's own
isolation is sufficient** (Amendment 4, §13).

A deterministic validation step (reused across both repos, part of the
deliverable list, §17 item 4, a real `scripts/`-level script, not a
one-off manual confirmation, §19) fails the branch outright if **any**
of the following holds:

1. A path matching the EXCLUDE list is present anywhere in the tree.
2. A path exists in the tree that is not covered by either the ALLOW
   list or the handoff package itself (an unlisted writer-visible path).
3. A path named in `included_paths` is missing from the actual tree.
4. Any `intermediary_projection_hashes` entry does not match a fresh
   re-hash of the corresponding canonical render.

The branch therefore represents, verifiably, **exactly** what the
clean-room writer is permitted to know — not an approximation a reviewer
has to infer from reading the tree.

### 6.1.2 Two trust boundaries, named explicitly (Amendment 8)

Everything in §9 ("preparation") and everything in §6.1/§6.1.1 ("the
writer's own boundary") sit on opposite sides of one line, stated here
once so no later section has to re-derive it:

```
PREPARATION SIDE                       WRITER SIDE
----------------                       -----------
orchestrator may inspect:              writer sees only:
  old docs (README/docs/architecture/    allowlisted source/tests/
    ai-docs/docs/domain, §7/§9.1)          config/schema (§6.1.1 ALLOW)
  current source/tests/config            validated intermediary handoff
  decisions/** (full ADR history)          (§8)
  canonical knowledge                    CLEANROOM-INSTRUCTIONS.md /
  project history (retros, ROADMAP)        DOCUMENTATION-TARGET.md
purpose:                               writer does NOT see:
  identify current truth                 old project documentation, in
  find gaps                                any form, original or
  enrich intermediary knowledge            synthesised-but-still-prose
  prepare the clean-room handoff         the original repository
                                          project/decision history
```

This is what lets CodeCompass genuinely learn from its own prior
documentation — using it freely, on the preparation side, to find gaps
and verify terminology — **without** letting the fresh writer anchor on
it. Every subsequent section's own "old docs are preparation-only, never
writer-visible" language (§7, §9.1, §9.5, §15) is a restatement of this
one boundary, not a separate rule each time.

### 6.2 Mode B — the actual isolation boundary

A workspace derived from the branch via `git archive
cleanroom/redoc-<revision> | tar -x -C <isolated-dir>` — a plain
filesystem tree with **no `.git` directory at all**, not a shallow
clone. A shallow clone is explicitly insufficient (per the governing
request) if the clone still has a working remote or reachable object
database pointing at the real repository; `git archive`'s own output has
no `.git` at all, closing that route by construction rather than by
configuration.

If the writer tool itself wants a local Git history for its own
convenience (some agents work better with a real repo), a **fresh**
`git init` + one commit of the archived tree, inside the isolated
directory, is permitted — explicitly a *new*, disconnected history with
no ancestry to the source repository, never a clone or fetch from it.

### 6.3 Verified Mode B isolation — a hard prerequisite, not one of several acceptable outcomes (Amendment 1)

**Corrected by the second revision.** The first-committed version of this
plan treated `best-effort`/`UNMET` as an acceptable terminal label for
Mode B, consistent with Phase 79/80's own narrower charter. On review
this was wrong for Phase 81B specifically: this phase's entire value
proposition is an *authoritative* redocumentation run that genuinely
could not have seen old documentation or the source repository — a
`best-effort` run does not establish that, it only establishes compliant
behaviour under an unenforced instruction (exactly the distinction
`isolation-evidence-inventory.md` already draws). The required state
machine is now:

```
attempt isolation
      ↓
active isolation tests pass (every route in §21, actively, not passively)
      ↓
VERIFIED MODE B
      ↓
cold-reader gate, inside verified Mode B (§13, Amendment 4)
      ↓
clean-room writer, inside verified Mode B (§6.4)
      ↓
complete re-doc
```

```
attempt isolation
      ↓
UNMET / best-effort
      ↓
Phase 81B BLOCKED
      ↓
do not run the authoritative clean-room writer
```

**A failed isolation attempt is valid evidence and must be recorded
honestly** (§21, §18) — it is simply not sufficient for Phase 81B's own
completion. If `best-effort` is all that can be achieved, Phase 81B
remains `blocked`/`in progress`, not `done` (§18); the workflow mechanism
and both redocumentations are not separately "completed anyway" under a
downgraded isolation claim, because the authoritative writer run itself
may not proceed without `VERIFIED MODE B` — there is nothing left to
complete.

**Investigation procedure, as implementation's own first concrete step**:
run the full five-route preflight (filesystem/search/command/network/
delegation, `decisions/0066`) plus the backlog item's own required
*active escape attempts* (point 4 of
`strict-isolation-for-documentation-reconstruction.md`) against the
`unshare --net --mount --pid --fork`-based candidate (§1.4), inside the
real environment the writer will actually run in, covering every route
named in §21. Three possible investigation outcomes, each reported
honestly, only one of which authorises proceeding:

1. **The mechanism holds for every route, including an AI writer that
   needs network access only to its own model provider** (resolved via
   a scoped egress allowlist — e.g. a network namespace with only the
   model API's own host/IP routable, confirmed to still deny every other
   destination including `github.com` and any configured Git remote) —
   `VERIFIED MODE B`. **Proceed** to the cold-reader gate and writer run.
2. **The mechanism holds for filesystem/search/command/delegation but
   network egress cannot be safely scoped for an AI writer** — Phase 81B
   uses a **fully offline/local writer** (no network dependency at all —
   a human, or a locally-hosted model with no outbound capability) or a
   human-in-the-sandbox writer operating the isolated shell directly with
   network revoked, so that the *authoritative* run is genuinely
   `VERIFIED`. **Proceed** only via one of these two paths; an AI writer
   still requiring unscoped network is not an authoritative run and does
   not satisfy this gate.
3. **No reliable enforcement can be established with the `unshare`-based
   candidate** — this is not the end of the investigation. Per the
   governing request: **investigate a different execution substrate
   rather than silently downgrade the clean-room claim** — e.g. a
   container runtime if one becomes available, a genuinely separate
   worker machine, or another mechanism satisfying §21's own requirements.
   Only once every substrate reasonably available in the real environment
   has been tried and failed is the honest conclusion `UNMET`, recorded
   plainly (§18, §21, the stored workflow §19, and the phase retro) —
   and Phase 81B is **blocked**, not closed, on that conclusion.

This plan deliberately does not pre-select outcome 1, 2, or 3 — that
determination is implementation's own job, tested, not planning's job,
assumed. What has changed from the first-committed version is not the
investigation itself, but what each outcome *authorises*: only outcome 1
or 2 authorises the authoritative writer run; outcome 3 blocks it.

### 6.4 Writer filesystem

Inside the isolated workspace: `/evidence` (read-only — the exact
`git archive` output, nothing added afterward) and `/output` (writable —
where the writer places `README.md` and `docs/**`). The writer may
freely run local project commands against `/evidence` (test suite,
`--help`, static search) where doing so cannot defeat isolation (no
network-backed command, no symlink escape out of `/evidence`) — the
preflight (§21) explicitly tests this boundary, not just the obvious
filesystem-read route.

---

## 7. Documentation inventory and disposition

### 7.1 Classification (maps onto `documentation-lifecycle.md` §1's existing three roles)

**Corrected by the second revision (Amendment 2/7).** The first-committed
version of this plan carved `docs/domain/**` out of disposition entirely,
reused unchanged as writer-visible evidence. On review this was wrong:
it is still human-facing narrative prose, and Phase 81B is a *full*
re-doc — no category of current narrative documentation is implicitly
exempt merely because it was previously judged accurate. The table below
reflects the corrected classification.

| This phase's label | Maps to `documentation-lifecycle.md` | Examples found in §1.2 |
|---|---|---|
| CURRENT STRUCTURAL/EVIDENCE INPUT | §1.1 current truth (non-narrative only) | current `src/`, tests, config, schemas, CLI `--help`, protocol/interface source — never a prose `.md` file, see §6.1.1's own ALLOW list |
| CURRENT NARRATIVE DOCUMENTATION — every item gets an explicit disposition, none exempt | §1.1 current truth, *and* §1.4's domain category | `README.md`'s own narrative prose; `architecture/overview.md`/`core-data-model.md`/`sync-and-enrichment-pipeline.md`/`adapter-interface.md`/`module-map.md`; `docs/cli-reference.md`, `docs/config-schema.md`, `docs/quickstart.md`, `docs/external-adapters.md`, `docs/protocol-adapter/**`, `docs/developer/**`; `ai-docs/**`; **`docs/domain/**`** (Phase 63D/79/80's own evidence-backed corpus — its *semantic content* is genuinely valuable and is preserved via re-grounding into validated knowledge, §9.1, but the files themselves are narrative prose like any other and are reconstructed/replaced, deleted, or archived, never silently carried forward unchanged) |
| HISTORICAL / GOVERNANCE RECORD | §1.2 decision history, §1.3 historical milestone state | `decisions/**` (append-only, never touched by this phase); `planning/retros/**`; `planning/ROADMAP.md`/`CONTEXT.md`; every ADR; `architecture/historical-notes.md` (see §7.2 — a genuine edge case) |

`docs/domain/**`'s own disposition is therefore decided the same way as
every other narrative file (§7.4) — most likely **reconstructed**
(its semantic content re-expressed inside the fresh writer's own new
docs tree, grounded via the Claim/Evidence pipeline, §9.1) rather than
deleted outright, since the underlying meaning remains genuinely current
— but that is a real disposition-report decision (§8.3), made with
evidence, not a standing exemption decided here. Phase 64's own "domain
terminology is not rederived from scratch" exception
(`documentation-lifecycle.md` §3) is about not re-litigating *what
concepts mean* — it was never a license to show the writer the original
prose, and this plan does not read it that way.

### 7.2 `architecture/historical-notes.md` is a named edge case, resolved explicitly

It is currently kept **inline** in the normal `architecture/`
navigation, deliberately historical in content but not removed from the
reader's path — a different convention from what this phase proposes for
newly-identified superseded documentation (§7.3's own navigation rule).
Phase 81B's implementation must decide, during the disposition pass, one
of: (a) leave it exactly as is (it already satisfies "clearly marked as
historical," just not "out of the navigation path," and its own two
narrated incidents remain genuinely load-bearing for understanding
current code, per its own stated rationale) — the likely outcome, since
rewriting a page that already works correctly for a different, narrower
reason than this phase's own disposition work is unnecessary scope; or
(b) if the fresh writer independently finds a cleaner place for that
content, fold it in and archive the original. This is a **disposition
report line item** (§8.3), decided during implementation with real
evidence, not pre-decided here.

### 7.3 Archive location and rule

No archive directory convention currently exists in either repository
(confirmed by investigation, §1). Phase 81B establishes one:
**`docs/archive/`** for CodeCompass, **`docs/archive/`** for
`codecompass-template` (consistent naming across both; a lighter
directory for the template given its much smaller doc set). Every
archived file:

- Carries a one-line banner at its own top: `> **Historical.** Not
  current documentation. Not an implementation or reference source. See
  <replacement doc> for current information.`
- Is **not** linked from `README.md`, `docs/`'s own index/navigation, or
  any current-truth page's normal reading path — reachable only by
  direct path or a single, explicit "historical material" pointer (one
  line, one place), never folded into a large searchable archive
  presented as equivalent to current docs.
- Is listed in the disposition report (§8.3) with its reason for
  archival rather than deletion.

Deletion is preferred by default (§7.4) — archival is the exception, not
the default outcome, per the governing request's own "do not use a
large searchable archive as a substitute for making documentation
decisions."

### 7.4 Delete vs. archive vs. preserve-as-governance — decision rule

- **Delete** when the replacement documentation fully supersedes it, Git
  history already preserves the superseded version (true for every
  tracked file in this repository), and no runtime/build/governance
  requirement reads it. Expected default for most of §7.1's "superseded
  narrative" row.
- **Archive** only for genuine historical/governance/process value that
  does not fit `decisions/`/`planning/retros/` (which already have their
  own home) — e.g., a narrative explanation of a past design that is
  itself interesting evidence of project reasoning, not merely old prose
  about current behaviour. Expected to be a small minority of files, not
  a default.
- **Preserve as governance/evidence, unconditionally, never deleted by
  this phase**: `decisions/**`, `planning/retros/**`, `planning/learnings/**`,
  `planning/knowledge/**`'s own canonical records (only the *rendered
  projections* are regenerated; the canonical `.yaml` records are Phase
  81's own domain, untouched here except via the normal reconciliation
  loop in §9), `planning/ROADMAP.md`, `planning/CONTEXT.md`. These are
  not "Markdown documentation" for this phase's own purposes — they are
  the separate provenance/governance layer the governing request
  explicitly names, and Markdown-ness alone is never grounds for
  deletion.

---

## 8. Documentation handoff and disposition artefacts

### 8.1 Handoff package structure (CodeCompass)

```
planning/documentation-handoff/
    README.md                        -- what/why/how for the writer
    INDEX.md                         -- map of everything else in this dir
    SOURCE-OF-TRUTH.md                -- evidence hierarchy, conflict handling
    DOCUMENTATION-TARGET.md           -- required output structure (§12)
    OPEN-QUESTIONS.md                 -- carried from open-questions-and-conflicts.md

    knowledge/
        overview.md                        -- reference into rendered codecompass-domain/intermediate/overview.md
        invariants-and-constraints.md      -- reference/synthesis
        interfaces-and-behaviours.md       -- reference/synthesis
        workflows-and-state-transitions.md -- curated synthesis (see §8.2)
        edge-cases-and-compatibility.md    -- curated synthesis (see §8.2)
        tests-and-acceptance.md            -- reference into rendered tests-and-acceptance.md
        decisions-and-rationale.md         -- synthesis over decisions/*.md (titles/status/one-line rationale only)
        source-and-evidence-map.md         -- new, see §9.4
```

A parallel, much lighter `planning/documentation-handoff-template/` is
built for `codecompass-template` (§11).

### 8.2 "Reference/synthesis," not duplication — a concrete rule

Per the governing request's own instruction ("prefer references/
syntheses of canonical intermediary projections rather than
uncontrolled duplicate copies"): `knowledge/overview.md`,
`invariants-and-constraints.md`, `interfaces-and-behaviours.md`, and
`tests-and-acceptance.md` are **not new render targets** —
`knowledge_intermediate.py`'s own `_file_for_record` dispatch and five-
file render set are unchanged by this phase (no schema/renderer change,
consistent with Phase 81's own "zero new persisted fields" discipline
extended here to "zero new render-target proliferation" for the same
reason: adding render targets this phase does not need would be scope
creep this plan explicitly avoids). Each of those four handoff files is
a short pointer plus the *actual*, current rendered content, copied in
at handoff-build time from the real `planning/knowledge/<slug>/intermediate/*.md`
— frozen at build time (hash recorded in the manifest, §6.1), not a live
symlink, so Mode B's own `/evidence` stays genuinely read-only and
self-contained with no live dependency on the original repository tree.

`workflows-and-state-transitions.md` and `edge-cases-and-compatibility.md`
have no dedicated canonical render target (today's renderer folds
`workflow`/`state_transformation`-tagged Claims into
`interfaces-and-behaviours.md`, and there is no dedicated edge-case
category at all). These two are genuinely **curated syntheses**, built
by selecting and reorganizing already-existing canonical Claims (filtered
by `assertion_kind` and by content, not freshly authored prose) —
produced by `knowledge-curator`'s existing context-packet-assembly mode,
reused rather than reinvented, with the selection criteria themselves
recorded in `INDEX.md` for auditability.

`decisions-and-rationale.md` is a synthesis over `decisions/*.md` —
title, current status, and the rationale's own one-line summary per
ADR, explicitly **not** the full ADR text or its own historical
amendment chain (the writer gets "what was decided and roughly why," not
the project's full decision-history narrative, which belongs to
`decisions/` itself as a governance artefact, §7.4).

### 8.3 Disposition report

`planning/documentation-handoff/DISPOSITION-REPORT.md` (CodeCompass),
`planning/documentation-handoff-template/DISPOSITION-REPORT.md`
(template), one row per pre-existing documentation file:

```
| path | classification | final action | reason | replacement | archive location | refs to update |
```

Built **before** either clean-room branch is frozen (so the handoff
itself can be verified never to include a file this report classifies as
superseded narrative) and checked again at integration time (§16) to
confirm every row's "final action" actually happened in the real tree —
a maintainer must be able to answer "what happened to every documentation
file that existed before the re-doc?" by reading this one file, and the
independent Phase 81B audit (§18) checks every row against the real
repository state, not against the report's own say-so.

---

## 9. Complete intermediary export — preparation stage

1. **Reconcile** every pending knowledge-layer edit across all five
   CodeCompass-relevant slugs (`codecompass knowledge select-candidates`/
   `apply`, and `doc-select-candidates`/`apply` for the grounded
   `README.md` region) — no stale candidate left pending when the
   export freezes.
2. **Validate** (`scripts/check_knowledge_base.py --strict`,
   `scripts/check_user_docs.py --strict`) clean before proceeding.
3. **Enrich materially missing coverage** — per §1.1's own finding, most
   `codecompass-domain` Claims carry no `assertion_kind` at all. A
   dedicated, evidence-grounded pass (reusing `context-researcher`'s
   existing behaviour-first methodology, never guessing) classifies each
   currently-unclassified Claim against the project's real current
   behaviour, assigns a real `assertion_kind` from the existing closed
   enum where the evidence genuinely supports one, and leaves a Claim
   unclassified (not forced into a guessed category) where it doesn't.
   **Never fabricate a record merely to populate an empty category** —
   if CodeCompass genuinely has no recorded Decision/Requirement-shaped
   knowledge for some area, the handoff says so honestly (via
   `OPEN-QUESTIONS.md`), it does not get a manufactured one.
4. **Render every slug** fresh (`codecompass knowledge render`) against
   the now-enriched canonical knowledge, for all five slugs (first-time
   render for the three previously unrendered ones) — for repository-
   wide consistency, independent of which slugs are later selected for
   any one handoff (§9.6).
5. **Run the new projection-drift check (§10)** clean — no committed
   projection may be stale relative to its own canonical records at
   freeze time, across all slugs.
6. **Select** (§9.6) which validated, rendered slugs are documentation-
   relevant for this handoff, with the selection criteria recorded.
7. **Freeze** — hash every *selected* slug's rendered files into the
   manifest (§6.1) as `handoff_selected_slugs`/`intermediary_projection_hashes`;
   `all_rendered_knowledge_slugs` records the full set validated in steps
   4–5, whether or not selected.

### 9.1 What "complete" means here, concretely

The governing request's own coverage list (overview/purpose/terminology;
architecture/components; invariants/constraints; interfaces/behaviours;
workflows/state-transitions; edge-cases/compatibility; tests/acceptance;
decisions/rationale; limitations; open-questions/conflicts; source/
evidence-map) is covered by: the five rendered canonical files (items 1,
3, 4, 7, 10 above map directly); the two curated-synthesis handoff files
(§8.2, items 5–6); the decisions-and-rationale synthesis (item 8); a new
`source-and-evidence-map.md` (§9.4, below).

**Limitations — corrected by the second revision (Amendment 2).** The
first-committed version of this plan said limitations would be "carried
forward honestly from whatever the current `README.md`'s own
'Limitations' section... already states" — this is exactly the
old-prose-reaches-the-writer route Amendment 2 closes. Corrected
procedure: the orchestrator, on the preparation side only (§6.1.2), may
read the current `README.md`'s "Limitations" section as a **prompt for
where to look**, then independently re-verifies each candidate limitation
against real current source/tests/configuration/decisions, and only a
limitation that survives that verification becomes a genuine Claim (or an
`OPEN-QUESTIONS.md` entry if evidence is inconclusive) that the writer
receives through the ordinary knowledge pipeline — never the old
sentence itself, paraphrased or otherwise. A limitation the old README
states but current re-verification cannot confirm is not carried
forward at all; one current re-verification finds that the README never
mentioned is added as a new Claim. This is distinct from
`open-questions-and-conflicts.md` (§8.1's own `OPEN-QUESTIONS.md`), which
is one of Phase 81's own five rendered canonical files — already
grounded in real Claim/Evidence records by construction, not
pre-existing narrative prose — and so flows into the handoff the same
way `overview.md`/`interfaces-and-behaviours.md` do (§8.2), no
re-derivation step needed for content that is already canonical.

### 9.4 Source-and-evidence map — new handoff content, not a new canonical artefact

A short, generated (not hand-written) index: for each rendered Claim
shown to the writer, where its own supporting Evidence ultimately
grounds it (a `source_ref`/`doc_ref`/`test_ref` path, or an explicit
"declared, not yet evidenced" marker for a `proposed_policy`/intent-basis
Claim). Built mechanically from the existing Evidence records' own
already-reliable scalar fields (`decisions/0066` point 5 already
confirms these are "simple scalar strings, confirmed reliably
parseable") — no new schema, a generation script, not a new persisted
field.

### 9.5 `codecompass-template`'s own intermediary preparation (corrected by the second revision — Amendment 5)

`codecompass-template` has no `planning/knowledge/` of its own (it is a
scaffold, not a knowledge-bearing project), so there is no canonical
record set to render from — but **the first-committed version of this
plan was wrong to synthesise its intermediary export directly from
`docs/architecture.md`, `docs/worked-example.md`, and `README.md`**,
since those are exactly the narrative files Amendment 2/5 now excludes
from writer visibility. A direct synthesis from prior narrative prose
would risk converting old documentation into slightly reorganised new
documentation — precisely the outcome this amendment exists to prevent.

Corrected procedure, applying the same preparation/writer boundary as
CodeCompass itself (§6.1.2):

- **Structural/product evidence** (potentially valid clean-room
  evidence, allowlist-eligible): the actual directory structure;
  workflow/template files themselves (the nine clean-room workflow
  templates, the `optional-intermediate-knowledge/` files as
  *structural* artefacts); configuration/scaffold files
  (`vendor.toml`, `.gitignore`); any scripts; any tests; example
  artefacts that are executable/structural rather than explanatory prose;
  licence/package metadata (`LICENSE`, `CLAUDE.md`'s own structural
  routing content where it is genuinely instructional-for-a-tool rather
  than narrative-for-a-human).
- **Prior narrative documentation** (preparation-only, never
  writer-visible): `README.md`, `docs/architecture.md`,
  `docs/worked-example.md`, and any other explanatory Markdown
  (adoption guides, prose inside the clean-room/intermediate-knowledge
  guides that explains *concepts* rather than defining a *template
  structure*). The orchestrator may read these to discover intended
  concepts, structure, and potential gaps — exactly like the
  CodeCompass-side preparation step — but any content carried forward
  must first be independently grounded against the structural/product
  evidence above and expressed as a provenance-aware intermediary
  note (a short, generated synthesis analogous to
  `decisions-and-rationale.md`, §8.2, not a copy), before it can enter
  the handoff.

The template's own redoc therefore demonstrates that the Phase 81B
method is portable even when the target repository is itself
documentation-heavy relative to its code — the exact case where the
temptation to launder old prose into new prose is strongest, and exactly
why this amendment exists.

### 9.6 Render everything, include only what's documentation-relevant (Amendment 6, new)

Two distinct steps, previously conflated:

```
all knowledge slugs
      ↓
render + validate, for repository consistency (§9 items 1-5 — every
  slug, no exceptions: this is about catching stale/uncoherent canonical
  knowledge project-wide, not about what a writer sees)
```

```
documentation-relevant validated knowledge
      ↓
explicit selection
      ↓
clean-room handoff (§8)
```

**A slug is never included in the handoff merely because it exists and
was rendered.** For CodeCompass's own five slugs: `codecompass-domain`
(project-wide, almost certainly always selected) is the clear case;
`hledger-depth` (a Ledgerkit-relevant phase slug) and the three Phase
54c context-packet-research slugs (`doc-origin-pinned-reference`,
`first-party-source-symbols`, `haskell-api-surface-extraction`) are
selected only where their content materially helps explain the
*current* CodeCompass project to a fresh writer — e.g.
`first-party-source-symbols` genuinely describes a real, current
CodeCompass capability and is a reasonable candidate; `hledger-depth` is
about a specific reference-project engagement and would need a concrete
justification (not just "it exists") to belong in a project-level
redoc's own handoff, as opposed to a phase-scoped context packet where it
clearly belongs.

The selection criteria actually applied, and the resulting
`handoff_selected_slugs` list, are persisted in both the manifest
(§6.1) and the handoff's own `INDEX.md` (§8.1) — a reviewer can see not
just *what* was selected but *why*, and confirm nothing was included
"because it was there" rather than because it serves the writer's actual
task.

---

## 10. Generated-projection-drift protection (new deliverable)

Confirmed by investigation (§1.5): no existing check compares a
committed `intermediate/*.md` file's own content against what the
current renderer would produce right now — `check_anchor_integrity`
checks structural resolution only, and says so in its own docstring
("the anchor's own semantic/projection hashes are reconciliation's own
concern... not this structural check's"). A new check,
`check_no_pending_reconciliation` (added to `scripts/check_knowledge_base.py`,
same fail-closed discipline, same file per `CLAUDE.md` §1's own
"same file, not a new script" convention already established for this
project's checkers), re-runs `detect_anchor_changes` for every slug in
read-only mode and fails `--strict` if any anchor is currently
classified `refresh` or `candidate` (i.e., something reconcilable is
pending and the committed projection has not caught up) — explicitly
**not** failing on a legitimate, not-yet-reviewed `candidate` sitting in
a live `## Candidate additions` region (a human/tool-authored addition
mid-review is not drift, it's an open contribution) and explicitly
preserving a `semantic_change: false`-accepted presentation override
(the presentation cache, not the canonical record, is what "current"
means for a wording-only acceptance — unaffected by this check, per
Phase 81's own presentation/semantics split). This is exactly the
behaviour the governing request's §18 describes; it is a straightforward
extension of code Phase 81 already wrote (`detect_anchor_changes`,
`refresh_safe_anchors`), not a new mechanism.

---

## 11. `codecompass-template`'s own lifecycle — intentionally lighter

Same five-stage shape (handoff → branch → isolated workspace → writer →
verification → integration), run separately, with its own branch
(`cleanroom/redoc-template-<revision>`) and its own, much smaller
handoff (§9.5, §8.1's template variant). Documentation-target scope
(§12.2): purpose of the template; adoption process; directory/workflow
conventions; optional vs. required pieces; the Scope→Plan→Domain→
Design→Implement workflow shape; the clean-room documentation workflow
itself (a pointer to CodeCompass's own now-durable process, §19 — the
template explains *that* this capability exists and how to invoke it for
a downstream project, it does not re-explain CodeCompass's own internal
governance history); the optional intermediate-knowledge workflow;
extension/adaptation points; assumptions/invariants; intentionally
unspecified choices. **Never** copies CodeCompass's own `decisions/`,
`planning/retros/`, or internal phase-numbering history into the
template — that governance history is CodeCompass's own, not a
downstream adopter's concern, consistent with the template's existing,
already-adopted MIT-licensed, CodeCompass-agnostic posture.

---

## 12. Full redocumentation deliverable, both repositories

### 12.1 CodeCompass — expected coverage (adapted from real evidence, not fixed in advance)

```
README.md

docs/
  getting-started.md
  concepts/              -- the fresh writer's own reconstruction of
                             domain meaning, grounded in the validated
                             intermediary knowledge handoff (§9.1), never
                             a pointer into or copy of the old
                             docs/domain/** prose (Amendment 2/7)
  architecture/
    overview.md
    components.md
    data-and-control-flow.md
  workflows/
  reference/
    cli.md
    configuration.md
    protocols.md
  development/
    contributing.md
    testing.md
    clean-room-redocumentation.md   -- the stored process itself, §19
```

The exact final structure is the clean-room writer's own evidence-based
finding, not a template this phase forces. **Corrected by the second
revision**: `docs/domain/**` is **not** expected to remain as-is — per
§7.1's own corrected classification, its own files receive an explicit
disposition like every other narrative document. The *meaning* those
files currently hold is expected to resurface inside the fresh writer's
own `docs/concepts/` (or wherever the writer's own evidence-based
structure puts it), because that meaning was already re-grounded into
validated knowledge before the handoff was built (§9.1) — but it arrives
there via the writer's own fresh reconstruction from supplied knowledge,
never via the old files themselves surviving untouched.

### 12.2 `codecompass-template` — lighter, adoption-focused (§11)

A smaller tree: `README.md`, a short `docs/` (adoption + architecture +
clean-room pointer + optional-workflow pointers), no `docs/domain/`
equivalent, no `architecture/` directory distinct from
`docs/architecture.md`. Its own current content — whatever the template
genuinely needs to say about adoption/structure/concepts — is **derived
fresh from structural/product evidence** (§9.5, Amendment 5), never
carried forward from the current `README.md`/`docs/architecture.md`/
`docs/worked-example.md` prose merely because those happen to already
say roughly the right thing.

### 12.3 Completion bar (strengthened, Amendment 7)

A full re-doc means **every** current human-facing narrative
documentation artefact in both repositories receives one explicit,
executed disposition: **reconstructed/replaced**, **deleted**, or
**archived as genuinely historical** — there is no category of current
narrative documentation implicitly exempt merely because it was
previously judged accurate (this is the corrected reading that also
closes §7.1/§12.1's own `docs/domain/**` gap). Concretely, both
repositories end with: a fresh `README.md`; a fresh, current
documentation tree covering the repository's real needs (**not** a
mechanical preservation of the old file/page boundaries — the final
structure may, and is expected to, differ from the previous one); every
row of the disposition report (§8.3) confirmed executed against the real
tree, with its recorded final action actually matching reality; no
competing legacy current-truth documentation anywhere in the tree;
historical material clearly separated into the archive location (§7.3),
never left in the normal reading path; every internal link/navigation
reference reconciled (`check_internal_links_resolve`, re-run clean,
§18).

---

## 13. Cold-reader acceptance test — must run inside verified Mode B (Amendment 4)

**Corrected by the second revision.** The first-committed version of this
plan permitted the cold-reader to run against "the Mode A branch
contents (or, if Mode B is ready, the actual isolated workspace —
whichever the implementation sequence reaches first)." This was wrong:
Mode A (§6.1) is review/portability only — a maintainer or trusted tool
checking out the branch from the ordinary repository, where normal Git
history remains reachable even if nothing in the branch's own tree
points at it. A cold-reader run under Mode A tells you the handoff
*looks* sufficient to something that could, technically, still reach
the original repository if it tried — which is not the same question as
whether the handoff is sufficient for something that technically
cannot. **A successful Mode A cold-reader must never be used as evidence
that the real clean-room handoff is sufficient.**

Corrected sequence:

```
prepare handoff branch
        ↓
Mode A human/trusted inspection (review only, §6.1 — never isolation
  evidence)
        ↓
create Mode B workspace (§6.2)
        ↓
prove Mode B isolation (§6.3/§21) — VERIFIED, not best-effort (Amendment 1)
        ↓
fresh cold-reader, dispatched INSIDE that same verified Mode B workspace
        ↓
handoff sufficient?
   ├── no  → back to §9 (knowledge preparation) / §9.6 (handoff selection)
   └── yes
        ↓
fresh documentation writer, inside an equivalent verified Mode B boundary
```

The cold-reader and the real writer therefore exercise **the same class
of isolation**, not merely the same handoff content — a cold-reader run
inside a different, weaker boundary than the real writer will use proves
nothing about the real writer's own run. For each repository: a fresh
reader (a separate agent dispatch, inside Mode B, or a human physically
confined to the isolated workspace with no other access — never the
orchestrator's own context, which already knows the old project)
answers the governing request's own bounded question set (what is this
project for; main architectural components; important interfaces;
principal workflows; invariants that must be preserved; what fails
closed; configuration/testing; where a contributor would modify X;
limitations/open questions). Every question, answer, cited evidence
reference, and any "insufficient context to answer" finding is persisted
(`planning/documentation-handoff/COLD-READER-REPORT.md`, noting the
isolation tier it ran under). **The full writer run does not proceed
until (a) Mode B is independently verified and (b) this report, produced
inside that verified Mode B, shows a materially correct project model**
— a genuine, two-part gate, not a formality; a finding here routes back
to §9's own enrichment step or §9.6's own selection step, not forward to
the writer.

---

## 14. Result branch and integration

Writer output (`/output/README.md`, `/output/docs/**`) is imported by
the orchestrator — never by the writer itself pushing to the original
repository, which would both weaken isolation and require credentials
the isolated workspace must not have (§6.3) — into
`cleanroom/redoc-<revision>-result` (CodeCompass) /
`cleanroom/redoc-template-<revision>-result` (template). Full
provenance chain, each link a real, inspectable Git artefact:
`SOURCE_REVISION` → handoff branch → isolated workspace (ephemeral,
not itself committed anywhere — its manifest and output are) → writer
output → result branch → verification report → disposition execution →
integration branch → `main`.

---

## 15. Separation of generation and verification (Amendment 9: verification stays informed, writer stays clean)

The writer (generation) never has full repository/canonical access —
that is the entire point of Mode B. **Verification is a separate pass,
by a different role, with normal access restored**: `domain-skeptic`'s
existing comparison mode (already classifies
`aligned`/`partial`/`conflicting`/`not_implemented`/
`insufficiently_verified`, reused directly, no new rubric) checks the
result branch's own claims against the new docs, canonical/intermediary
knowledge, source/tests/configuration/schemas, live CLI behaviour, **and
— explicitly permitted at this stage, unlike at the writer's own stage —
the old documentation and project history, where useful for identifying
omissions the writer couldn't have known to check for.**

**The old documentation's role at this stage is strictly bounded: comparison and history, never authority.** The verifier may notice "the old
docs described a configuration option the new docs omit" and use that as
a prompt to check whether the option still exists in real current
source/config — but the *verdict* on whether to include it is always
decided against current evidence, never because the old docs said so.
Old prose settles nothing by itself at this stage either; it only
suggests where to look.

Findings returned to a *further* writer round must be **factual and
bounded**, grounded in current evidence, e.g. "CLI option `--foo` is
documented incorrectly; verify `src/codecompass/cli.py:NNN` and correct
it" — **never** by relaying the old prose itself back to the writer, and
never phrased as "the old docs said X, please add X," which would
silently smuggle old documentation's own authority back into the
supposedly clean-room writer round. The writer's own isolation (Mode B)
is unaffected by what the verifier itself was allowed to see — the
boundary is on what reaches the writer, not on what the verifier may
consult to find a finding worth sending.

---

## 16. Superseded-document cleanup, link reconciliation, final integration

Executed strictly from the disposition report (§8.3) — delete/archive
exactly what it says, nothing it doesn't, verified against the real tree
afterward (not merely trusted). `check_internal_links_resolve` and
`check_no_deleted_names_as_live` (both already exist,
`scripts/check_user_docs.py`) re-run clean on the integrated tree before
Phase 81B can be considered for closeout.

---

## 17. The process itself is a Phase 81B deliverable — sequencing, explicit

```
Phase 81B exercise (this phase's own full run, both repositories)
        ↓
learn / amend workflow (real findings from the real runs — e.g. what the
  §6.3 isolation preflight actually found, what the cold-reader gate
  actually caught, what disposition edge cases §7.2-style items turned
  up)
        ↓
final approved workflow (explicit sign-off that the *exercised and
  corrected* procedure, not the original untested plan, is authoritative)
        ↓
persist workflow in repository: docs/development/clean-room-redocumentation.md
  (CodeCompass's own chosen durable home, per the governing request's own
  suggested default location — confirmed consistent with this project's
  existing docs/development/-adjacent convention, `documentation-lifecycle.md`
  §1.4 category 4, "Developer")
        ↓
future repeatable redocumentation runs, from repository instructions
  alone, no conversational knowledge required
```

**This plan does not pre-freeze the untested procedure above as the
final stored document.** `docs/development/clean-room-redocumentation.md`
is written **near the end** of implementation, once both repository
exercises are complete and findings incorporated (per the governing
request's own instruction) — it documents the actual proven procedure:
commands actually run, the actual branch lifecycle, the actual
manifest/file shapes, the actual isolation mechanism and its actual,
honestly-achieved tier (`VERIFIED` — per Amendment 1, the only tier under
which "both repository exercises are complete" can even be true, §18),
actual evidence-preparation steps, actual disposition rules applied,
actual cold-reader check results, the actual writer invocation contract,
actual verification and integration steps, deletion/archive rules as
applied, validation commands, and failure/retry behaviour observed.
**If Phase 81B is instead `blocked`** (§6.3 outcome 3 — no substrate
achieved `VERIFIED`), no such document is written as a completed,
repeatable process yet; the investigation itself (what was tried, what
failed, why) is still recorded honestly in the retro and left as a
pointer for a future attempt, exactly as Phase 79/80's own `UNMET`
findings were recorded without being dressed up as a finished capability.
If reusable scripts are written during implementation (the branch-manifest validator,
§6.1; the projection-drift checker, §10; any export/import helper), they
live under `scripts/` and are referenced by the stored document, not
left as one-off manual commands.

---

## 18. Phase 81B's own Definition of Done (rewritten, Amendment 10)

**Corrected by the second revision.** The first-committed version's own
item 4 allowed `best-effort`/`UNMET` to satisfy the isolation condition.
Per Amendment 1 this is no longer a satisfiable terminal state —
completion requires all sixteen of the following:

1. Canonical/intermediary preparation complete (§9 items 1–3).
2. Every relevant projection rerendered and drift-clean (§9 items 4–5,
   §10) — all slugs, per §9.6's own render-everything discipline.
3. Documentation-relevant handoff selection explicit — selection
   criteria and chosen slugs/ids recorded in the manifest and `INDEX.md`
   (§9.6, Amendment 6), never "everything that exists."
4. Clean-room branch manifests validated for both repositories — the
   explicit allowlist/exclusion list (§6.1.1) matches the real tree
   exactly; no excluded path present, no unlisted path present, no
   listed path missing, every intermediary hash matching a fresh
   re-render.
5. **Mode B isolation `VERIFIED`** (§6.3/§21) — every active escape
   attempt against every named route genuinely failed. Not assumed, not
   inferred from a tool's own description, not satisfied by
   `best-effort`.
6. Cold-reader run **inside that same verified Mode B** and passed
   (§13, Amendment 4) — a Mode A or orchestrator-context cold-reader run
   does not satisfy this condition.
7. Full clean-room reconstruction executed **inside verified Mode B**
   for CodeCompass (§12.1) — not merely mechanism-proven, not a partial
   or example run.
8. Full clean-room reconstruction executed **inside verified Mode B**
   for `codecompass-template` (§12.2, §9.5/Amendment 5's own
   narrative/structural separation genuinely applied, not merely stated).
9. Independent, informed verification (§15) passed, or every finding it
   raised resolved by a further, still-isolated writer round.
10. **Every** previous human-facing narrative documentation artefact in
    both repositories has an *executed* disposition — reconstructed/
    replaced, deleted, or archived — confirmed against the real tree, not
    merely claimed in a report. No category (including `docs/domain/**`
    or any file previously judged accurate) is implicitly exempt
    (Amendment 2/7).
11. Old and new current-truth documentation do not coexist anywhere in
    either tree.
12. Navigation/internal links clean
    (`check_internal_links_resolve`/`check_no_deleted_names_as_live`,
    re-run clean, §16).
13. The final, *actually exercised* workflow persisted in-repo
    (`docs/development/clean-room-redocumentation.md`, §17/§19) —
    reflecting what was proven, including the real isolation mechanism
    and tier achieved, not the original plan's own untested procedure.
14. Full test suite, lint, strict knowledge-base/user-docs validation
    all clean.
15. Per-phase docs-drift audit (`docs-reconstructor`), learning/
    context-gap triage (`knowledge-curator`), a full-`TEMPLATE.md`-shape
    phase retro, and an independent `release-phase-auditor` completion
    audit — all complete, the audit explicitly inspecting: whether the
    writer genuinely lacked `main`/old-documentation access for whatever
    tier was claimed; whether Mode A/Mode B/the cold-reader's own
    isolation tier were kept distinct and consistent in the actual
    implementation, not merely in this plan's prose; whether `verified`
    was asserted only where every active escape attempt genuinely failed;
    whether both repositories' redocumentation is actually complete, not
    partial; whether every disposition-report row's claimed action
    matches the real tree, with no narrative category silently exempted;
    whether the template genuinely avoided laundering its own old prose
    (Amendment 5); whether the stored workflow document is genuinely
    derived from what was proven.
16. `planning/ROADMAP.md`/`CONTEXT.md` reconciled **only after** every
    prior gate above genuinely passes — including the strict-isolation
    backlog item's own resolution (§20) — the terminal action, not a
    condition checked alongside the others, per `CLAUDE.md` §5's own
    established sequencing.

**If verified Mode B cannot be achieved** (§6.3 outcome 3, after
genuinely investigating available alternative substrates), **Phase 81B
remains `blocked`/`in progress`**, with the failed attempt(s) recorded
honestly in the retro and the stored workflow document. It is not marked
`done` on the strength of a best-effort clean-room run, no matter how
complete the rest of the mechanism is.

---

## 19. Tool independence

The branch + manifest + isolated-filesystem contract (§6) is the
invariant; the actual writer may be Codex Cloud, Codex CLI, Claude Code,
another coding agent, or a human operating the isolated shell directly.
Nothing in `CLEANROOM-INSTRUCTIONS.md` (§6.1, drafted from the governing
request's own §13 template) names a specific tool. Tool-specific
invocation detail (how to actually launch whichever tool against
`/evidence`+`/output`) is recorded as an implementation-time appendix to
§19's own stored document, not baked into the contract itself.

---

## 20. Relationship to the existing strict-isolation backlog item

Phase 81B's own implementation is, explicitly, the backlog item's own
named revisit trigger ("a third independent application of the
clean-room methodology," §1.3). `planning/ROADMAP.md`'s backlog row for
"Strict mechanical isolation for documentation-reconstruction stages" is
updated, in this planning commit, to link forward to Phase 81B as that
trigger (not yet resolved — resolution happens at Phase 81B's own
closeout, §18 item 16, once the real outcome of §6.3 is known). The
backlog item's own document
(`planning/strict-isolation-for-documentation-reconstruction.md`) is
**not** rewritten now.

**Corrected by the second revision, following Amendment 1**: the two
possible outcomes are no longer symmetric. If Phase 81B's implementation
genuinely achieves `VERIFIED` Mode B isolation, the backlog item is
formally resolved (closed, pointing at the new, real evidence) as part
of Phase 81B's own closeout — **and Phase 81B itself proceeds to
completion**, since `VERIFIED` is now the prerequisite for its own
authoritative writer run (§6.3/§18). If, after genuinely investigating
the `unshare`-based candidate and at least one alternative execution
substrate (§6.3 outcome 3), no mechanism achieves `VERIFIED` isolation,
the backlog item is updated with that third data point — but **Phase 81B
itself does not close** on that outcome. It remains `blocked`/`in
progress` (§18), with the honest `UNMET` finding, the investigation
record, and the (still-valuable, separately recorded) prepared handoff/
manifest/disposition-report work all preserved, pending either a future
re-attempt or an explicit decision by the user to accept a differently-
scoped completion. This is the one place amendment review (§24) found
this plan's own structure needs to be read carefully: a blocked Phase
81B is not a failed plan, and the preparation work it produces (§9, §9.6,
§7's own disposition reports) remains genuine, reusable progress even if
the authoritative writer run itself cannot yet proceed.

---

## 21. Security / isolation acceptance criteria (Amendment 1: now a hard gate, not an aspirational extension)

Builds on the backlog item's own already-specified criteria
(`strict-isolation-for-documentation-reconstruction.md`, "Acceptance
criteria") — but, corrected by the second revision, these are no longer
offered as one acceptable track among others (§6.3/§18): **point 1 below
must be satisfied, mechanically, before the authoritative writer run may
proceed at all.**

**`verified` means the actual writer cannot access**, confirmed by
**active** denied-access attempts (not passive, unused routes) against
every one of:

```
original repository filesystem
parent paths containing another checkout
original .git objects/history
main/other branches
Git remotes
public GitHub repository
network routes capable of rediscovering the project
credentials/tokens/SSH keys
MCP/connectors exposing source/history
agent/project context carrying old documentation
```

Concretely, each probed by direct attempt, not inference: filesystem
paths outside `/evidence`; parent-directory traversal; `.git` history/
objects (none should exist at all in the Mode B workspace, §6.2); other
branches; Git remotes; a direct attempt to resolve `github.com` and to
search for the public CodeCompass repo by name; environment variables;
credentials/SSH keys; MCP/connectors; and any agent/project shared
context that might expose old documentation (e.g. this very
conversation's own memory/context, explicitly named as an escape route
to test — a genuinely fresh dispatch or process must not inherit it).
**The enforcement must be mechanical — instruction-only compliance does
not qualify, no matter how many times it happens to succeed.** If the
locally investigated `unshare`-based mechanism (§1.4/§6.3) cannot satisfy
every route above, implementation must investigate another execution
substrate (§6.3 outcome 3) rather than silently downgrade the clean-room
claim to `best-effort`.

Further criteria, all still required:

2. A real manifest (§6.1/§6.1.1) for whatever was fed to the writer,
   confirmed sufficient by actually running the writer's own real
   workflow inside the verified boundary and getting a usable result —
   not merely confirming the boundary holds for an empty/trivial task.
3. For at least one of the two repositories, draft-before-reconciliation
   ordering (the fresh writer's own output exists as a committed result
   before any legacy-documentation reconciliation step runs) demonstrated
   mechanically — the reconciliation stage's own environment must not
   even contain the legacy documentation until after the draft's commit
   exists — not merely inferred from commit timestamps after the fact.
4. A written, final, four-way-separated verdict: isolation
   (`VERIFIED` — the only outcome that authorises proceeding — or
   `best-effort`/`UNMET`, which blocks, §18) / workflow completion /
   documentation accuracy / coding-context usefulness (if applicable) —
   never collapsed into one overall "done."
5. Independent `release-phase-auditor` completion audit (§18 item 15).

Where a route cannot be technically prohibited in the real environment
Phase 81B actually runs in, the stored workflow document (§19) names it
explicitly as a limitation, **and the authoritative writer run does not
proceed** — the limitation is not quietly absorbed into a lower-tier
"done" (§18). No claim of `verified` isolation is made anywhere (plan,
retro, ROADMAP, or the stored workflow) unless every probe and every
active escape attempt above genuinely failed.

---

## 22. Concrete deliverables list

1. Intermediary reconciliation/completeness pass (§9), including the
   honest `assertion_kind` enrichment (§9.3) and the new
   source-and-evidence-map generator (§9.4).
2. Projection-drift checker, `check_no_pending_reconciliation` (§10).
3. Documentation inventory/disposition mechanism and both repositories'
   disposition reports (§7, §8.3).
4. Clean-room branch preparation mechanism + manifest validator (§6.1).
5. Manifest format (`CLEANROOM-MANIFEST.yaml`, §6.1).
6. Handoff packages, both repositories (§8.1, §9.5, §11).
7. History-free filesystem export mechanism (`git archive`-based, §6.2).
8. Writer-isolation mechanism — investigated per §6.3/§21, honestly
   reported, whichever tier is actually achieved.
9. Writer instructions (`CLEANROOM-INSTRUCTIONS.md`, tool-independent,
   §19).
10. Cold-reader validation, both repositories (§13).
11. Full CodeCompass clean-room redocumentation, executed (§12.1).
12. Full `codecompass-template` clean-room redocumentation, executed
    (§12.2).
13. Reconstruction result branches + import mechanism (§14).
14. Informed verification, both repositories (§15).
15. Superseded-document deletion/archive, executed, both repositories
    (§16).
16. Link/navigation reconciliation, both repositories (§16).
17. Durable, in-repository, repeatable clean-room workflow document
    (`docs/development/clean-room-redocumentation.md`, §17, §19).
18. Final regression/acceptance checks (§18, §21).
19. Retrospection and independent audit (§18 items 13–14).

---

## 23. Design decisions still requiring explicit approval

**Corrected by the second revision.** The first-committed version's own
point 1 ("whether to pursue the `unshare`-based mechanism at all, versus
accepting `best-effort` upfront") is now moot — Amendment 1 makes
`VERIFIED` Mode B a hard prerequisite for the authoritative run, so
pursuing *some* genuinely isolated substrate is no longer optional; the
only open question is *which* substrate, resolved by the investigation
procedure itself (§6.3), not by a planning-time choice. Two points
remain genuinely undecided, named honestly rather than silently assumed:

1. **Archive location naming** (`docs/archive/` for both repositories,
   §7.3) — a reasonable default consistent with existing conventions,
   open to a different choice at approval time.
2. **Whether `architecture/historical-notes.md` is left untouched or
   folded into the new structure** (§7.2) — recommended default is
   "leave untouched," decided for real only once the clean-room writer's
   own findings exist.

Neither blocks approval of the plan as a whole — each has a stated,
reasonable default this plan proceeds with unless the approval response
says otherwise. **What is no longer open for discretion at
implementation time**: whether to accept `best-effort` isolation as
sufficient for the authoritative run (§6.3/§18/§21 make this a hard
no), and whether `docs/domain/**` or any other narrative file gets a
standing exemption from disposition (§7.1/§12.1 make this a hard no).

---

## 24. Plan-quality self-review (first-commit review, re-confirmed below; §24.1 is this amendment's own required second review)

- **Does the writer truly lack access to `main`?** Only once Mode B is
  independently `VERIFIED` (§6.3/§21, now a hard gate, Amendment 1) —
  explicitly never claimed for Mode A, which this plan repeatedly labels
  as review/portability, never isolation; and a `best-effort` outcome no
  longer authorises the authoritative writer run at all (§18).
- **Is branch portability confused with isolation anywhere?** No —
  §4's own lifecycle diagram and §6.1/§6.2 keep them as two named,
  distinct steps; §6's own opening principle states the distinction
  explicitly before either sub-section; §13 now explicitly forbids
  treating a Mode A cold-reader pass as evidence for the real handoff
  (Amendment 4).
- **Does Git history remain recoverable in the writer environment?**
  Not via `git archive` (§6.2) — no `.git` directory exists in the
  output at all; a fresh, disconnected `git init` is permitted but never
  a clone/fetch from the source.
- **Could network access rediscover the public repo?** This is the
  exact, named sub-problem of §6.3 — not claimed solved, and now a hard
  blocking condition rather than an accepted limitation: if no substrate
  closes this route, Phase 81B is `blocked`, not `done` (§18, Amendment 1).
- **Is intermediary knowledge sufficient?** Investigated directly (§1.1)
  rather than assumed — the real concentration-in-overview.md problem is
  named with real numbers, and §9.3's enrichment step addresses the
  measured root cause (missing `assertion_kind` classification) without
  fabricating anything; §9.6 now also makes explicit that "sufficient"
  means "deliberately selected," not "everything that was rendered"
  (Amendment 6).
- **Are stale generated projections prevented?** §10's new check, a
  direct, scoped extension of code Phase 81 already shipped.
- **Does old documentation really disappear from the writer's search
  surface?** Now unconditional, not tier-dependent: the writer never
  receives `README.md`/`docs/**`/`architecture/**`/`ai-docs/**`,
  including `docs/domain/**`, in any original or lightly-reorganised
  form (§6.1.1 EXCLUDE list, §7.1, Amendment 2) — confirmed by the
  branch validator's own fail-closed checks (§6.1.1), not merely by
  disposition-report ordering as the first-committed version claimed.
- **Do both repositories end with complete replacement docs?** §12.3's
  own explicit, strengthened completion bar (Amendment 7), checked at
  audit time (§18 item 7/8).
- **Does every superseded doc get an explicit disposition?** §8.3's
  report format plus §16's "verified against the real tree, not merely
  trusted" requirement — now explicitly including `docs/domain/**` and
  every other previously-exempted category (§7.1, Amendment 2/7).
- **Are archives genuinely historical, not a dumping ground?** §7.3's
  banner requirement, navigation-path exclusion, and "exception, not
  default" framing in §7.4.
- **Is the template workflow appropriately lighter?** §11, grounded in
  §1.7's own measured current template size — and now also genuinely
  clean-room, not merely lighter: §9.5's corrected structural/narrative
  split (Amendment 5) prevents the template's own old README/docs/
  worked-example prose from reaching its writer.
- **Does result import accidentally grant access back to the source
  repo?** §14 explicitly requires the orchestrator, not the writer, to
  perform the import — the writer never gains push access to anything.
- **Can another human/tool use the same handoff?** §19's tool-
  independence framing plus §6.1's Mode A review path — yes, by design.
- **Will the final proven workflow be durably stored and repeatable?**
  §17's own explicit sequencing (exercise → learn → final approved
  workflow → persist → repeat), §22 item 17.

### 24.1 Second-revision review — the seven named invariants (this amendment's own required check)

- **Isolation invariant** ("the authoritative writer cannot technically
  access the original repository, history, old docs, public repository,
  credentials or inherited project context") — satisfied by construction
  once §6.3/§21's own hard gate is read correctly: §18 item 5 makes
  `VERIFIED` a non-negotiable precondition for proceeding at all, and
  §3's own amended non-goals paragraph removes the old "best-effort is
  an acceptable result" escape hatch. **Confirmed satisfied by this
  plan's own text** — no remaining sentence anywhere in the document
  describes `best-effort`/`UNMET` as sufficient for the authoritative
  run (checked by re-reading §3, §6.3, §13, §18, §20, §21 together after
  amendment; the only remaining "best-effort" framing is
  `codecompass-template`'s own, separate, downstream-facing
  `mechanical-isolation.md` convention, §1.7, which this plan does not
  touch and which governs a different audience's own honest-reporting
  needs, not Phase 81B's own authoritative run).
- **Narrative-isolation invariant** ("no pre-existing human-facing
  project prose is visible to the writer") — §6.1.1's own explicit
  EXCLUDE list, §7.1's corrected classification (no standing exemption
  for `docs/domain/**`), §9.1's corrected limitations-handling, and
  §9.5's corrected template preparation (Amendment 5) together close
  every route this plan's own first-committed version left open.
  **Confirmed satisfied** — re-checked that no section still instructs
  copying prose into the handoff; every handoff file is either a
  canonical-render reference (§8.2, already evidence, not narrative) or
  an explicitly re-grounded synthesis.
- **Handoff invariant** ("every writer-visible file is explicitly
  allowlisted and recorded in the manifest") — §6.1.1's own ALLOW list
  plus the branch validator's four fail-closed conditions. **Confirmed
  satisfied.**
- **Cold-reader invariant** ("the cold-reader and full writer run within
  the same verified isolation class") — §13's own corrected sequence
  (Amendment 4), explicit that a Mode A or orchestrator-context
  cold-reader run never substitutes. **Confirmed satisfied.**
- **Reconstruction invariant** ("both repositories receive a genuinely
  fresh full documentation reconstruction rather than selective
  rewriting around preserved legacy prose") — §7.1/§12.1/§12.3's
  corrected "no implicit exemption" framing (Amendment 2/7). **Confirmed
  satisfied** — the one remaining place old content legitimately
  survives is *meaning*, re-grounded through the knowledge pipeline
  (§9.1), never original prose; this plan judges that distinction to be
  the correct line, not a loophole, since it is the same "verify, don't
  copy" discipline §9's own preparation stage already applies to every
  other knowledge source.
- **Template invariant** ("`codecompass-template` does not launder its
  old README/docs into the new docs through an intermediary summary") —
  §9.5's corrected structural-vs-narrative split (Amendment 5).
  **Confirmed satisfied.**
- **Repeatability invariant** ("the final exercised workflow, scripts,
  branch lifecycle, manifest format and validation commands are stored
  durably in CodeCompass for later use") — §17/§19/§22 item 17,
  unchanged by this amendment and re-confirmed still correct: the stored
  document is written *after* both exercises, from what was actually
  proven, not frozen now.

No invariant above required a structural redesign beyond the ten
amendments already made — each is satisfied by a correction already
present in a named section. (Had a further amendment been required by
this review, it would be recorded here rather than silently folded into
the sections above without a trace, consistent with this project's own
general preference for visible, explained revision over silent
rewriting.)

---

## 25. Non-implementation reminder

**This plan file, its roadmap/context updates, and nothing else, are the
only artefacts this task produces.** No clean-room branch exists. No
isolated workspace exists. No documentation has been read for disposal,
only inventoried by class in prose above. No `codecompass-template`
file has been touched. Implementation begins only on explicit approval
of this committed plan — e.g. "Approve Phase 81B and implement the
committed plan."
