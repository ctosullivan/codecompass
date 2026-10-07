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
| `docs/domain/` (19 concept pages + glossary/examples/etc.) | ~3,125 lines | Phase 63D/79/80's own evidence-backed domain corpus — **current structural/evidence input**, not narrative to be rewritten from zero |
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
isolation that the implementation did not actually demonstrate — an
honest `best-effort`/`UNMET` outcome for Mode B is an acceptable, correct
result (§21), not a phase failure, exactly as Phase 79/80 already
established.

---

## 4. Architecture — the lifecycle (as specified, grounded in real tool names)

```
main @ SOURCE_REVISION
        │  Preparation (§9): reconcile pending knowledge-layer edits
        │  (codecompass knowledge select-candidates/apply, every slug),
        │  validate (scripts/check_knowledge_base.py --strict), enrich
        │  materially missing assertion_kind/decision/requirement
        │  coverage (never fabricate), re-render every relevant slug
        │  (codecompass knowledge render), run the new projection-drift
        │  check (§10) clean.
        ↓
validated canonical knowledge (planning/knowledge/)
        ↓
complete intermediary export (rendered intermediate/*.md, all five
  CodeCompass-relevant slugs; a lighter equivalent synthesis for
  codecompass-template, which has no planning/knowledge/ of its own)
        ↓
documentation inventory + disposition decision (§7) — classify every
  existing docs/architecture/ai-docs/README file BEFORE building the
  handoff, so the clean-room writer is never shown superseded narrative
        ↓
clean-room handoff filesystem: planning/documentation-handoff/ (§11)
        ↓
durable clean-room Git branch: cleanroom/redoc-<source-revision> (§6)
        │
        ├──────── Mode A: git diff/checkout from the ordinary repo —
        │         human review, trusted-tool handoff, debugging (§6.1)
        │
        ↓
history-free isolated workspace, derived via `git archive` (§6.2),
  run inside the strongest mechanically-enforced boundary Phase 81B's
  own implementation can establish and prove (§6.3/§21) — honestly
  labelled `verified` or `best-effort`, never silently upgraded
        ↓
cold-reader acceptance check (§13) — gate before the full writer run
        ↓
fresh documentation-writing agent (tool-independent, §19) writing only
  to /output (§6.4)
        ↓
complete new README + docs from zero, per repository (§12)
        ↓
result branch: cleanroom/redoc-<revision>-result (§14)
        ↓
independent, informed verification (domain-skeptic comparison mode,
  full repository/canonical access) — supported/unsupported/
  contradicted/missing/insufficiently-evidenced (§15)
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

included_paths: [...]      # exactly what the handoff filesystem contains
excluded_paths: [...]      # named exclusions, so a reviewer sees what was
                            # deliberately left out, not just what's present

knowledge_slugs: [...]              # which planning/knowledge/<slug>/ fed this
intermediary_projection_hashes:     # slug -> {file: sha256}, so a reviewer can
  ...                               # confirm the handoff matches a specific,
                                    # frozen render, not a moving target

documentation_disposition: <path to the disposition report, §8.3>

network_policy: <what Mode B actually enforces, stated plainly — not aspirational>
history_policy: "none -- this filesystem has no .git directory, see §6.2"
credential_policy: "none -- no SSH keys, tokens, or env-var secrets included"
```

Mode A review is exactly `git diff <source-revision>...cleanroom/redoc-<source-revision>`
from the ordinary CodeCompass checkout — a maintainer sees precisely
what was added/exposed, nothing more. A deterministic validation step
(reused across both repos) confirms the branch's own tree matches its
own manifest byte-for-byte (every `included_paths` entry present, every
`intermediary_projection_hashes` entry matching a fresh re-hash,
`excluded_paths` genuinely absent) — this check is part of the
deliverable list (§17, item 4) and is itself a `scripts/`-level script,
not a one-off manual confirmation, so it is repeatable (§19).

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

### 6.3 The genuinely separate execution substrate — investigated, not yet proven (carries §1.4 forward into implementation)

Phase 81B's implementation must, as its *first* concrete step on this
front, run the full five-route preflight (filesystem/search/command/
network/delegation, `decisions/0066`) plus the backlog item's own
required *active escape attempts* (not just passive probing — point 4 of
`strict-isolation-for-documentation-reconstruction.md`) against the
`unshare --net --mount --pid --fork`-based candidate (§1.4), inside the
real environment the writer will actually run in. Three possible,
explicitly acceptable outcomes, reported honestly (§21):

1. **The mechanism holds for every route, including an AI writer that
   needs network access only to its own model provider** (resolved via
   a scoped egress allowlist — e.g. a network namespace with only the
   model API's own host/IP routable, confirmed to still deny every other
   destination including `github.com` and any configured Git remote) —
   label `verified`.
2. **The mechanism holds for filesystem/search/command/delegation but
   network egress cannot be safely scoped for an AI writer** — in which
   case Phase 81B either (a) uses a **fully offline/local writer** (no
   network dependency at all — a human, or a locally-hosted model with
   no outbound capability) for at least one genuinely `verified` run, or
   (b) falls back to a human-in-the-sandbox writer operating the
   isolated shell directly with network revoked — label `verified` for
   that run, `best-effort` for any AI-writer run that still needed
   unscoped network.
3. **No reliable enforcement can be established in the real environment
   this runs in** — label `best-effort`/`UNMET`, exactly as Phase 79/80
   did, and say so plainly in the final stored workflow (§19) and the
   phase retro. This is an acceptable phase outcome, not a blocker to
   closing Phase 81B (§17) — the workflow and both redocumentations must
   still be completed and are independently valuable even under
   `best-effort` isolation, matching `mechanical-isolation.md`'s own
   already-adopted principle.

This plan deliberately does **not** pre-select outcome 1, 2, or 3 — that
determination is implementation's own job, tested, not planning's job,
assumed.

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

| This phase's label | Maps to `documentation-lifecycle.md` | Examples found in §1.2 |
|---|---|---|
| CURRENT STRUCTURAL/EVIDENCE INPUT | §1.1 current truth, *and* §1.4's domain category | `docs/domain/**` (Phase 63D/79/80 evidence-backed corpus — reused as writer evidence, never rewritten from zero); current `src/`, tests, config, schemas, CLI `--help` |
| SUPERSEDED NARRATIVE DOCUMENTATION | §1.1 current truth, about to be replaced | `README.md`'s own narrative prose; `architecture/overview.md`/`core-data-model.md`/`sync-and-enrichment-pipeline.md`/`adapter-interface.md`/`module-map.md`; `docs/cli-reference.md`, `docs/config-schema.md`, `docs/quickstart.md`, `docs/external-adapters.md`, `docs/protocol-adapter/**`, `docs/developer/**`; `ai-docs/**` |
| HISTORICAL / GOVERNANCE RECORD | §1.2 decision history, §1.3 historical milestone state | `decisions/**` (append-only, never touched by this phase); `planning/retros/**`; `planning/ROADMAP.md`/`CONTEXT.md`; every ADR; `architecture/historical-notes.md` (see §7.2 — a genuine edge case) |

`docs/domain/**` is explicitly **not** superseded narrative — it is
Phase 63D's own dedicated, adversarially-reviewed evidence base for what
CodeCompass's concepts *mean*, reused by the clean-room writer as
supplied evidence (mirroring Phase 64's own "domain terminology is not
rederived from scratch" exception, `documentation-lifecycle.md` §3) —
never shown to the writer as an example of prose structure to imitate,
never deleted, never archived.

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
4. **Render every relevant slug** fresh (`codecompass knowledge render`)
   against the now-enriched canonical knowledge, for all five slugs
   (first-time render for the three previously unrendered ones).
5. **Run the new projection-drift check (§10)** clean — no committed
   projection may be stale relative to its own canonical records at
   freeze time.
6. **Freeze** — hash every rendered file into the manifest (§6.1).

### 9.1 What "complete" means here, concretely

The governing request's own coverage list (overview/purpose/terminology;
architecture/components; invariants/constraints; interfaces/behaviours;
workflows/state-transitions; edge-cases/compatibility; tests/acceptance;
decisions/rationale; limitations; open-questions/conflicts; source/
evidence-map) is covered by: the five rendered canonical files (items 1,
3, 4, 7, 10 above map directly); the two curated-synthesis handoff files
(§8.2, items 5–6); the decisions-and-rationale synthesis (item 8); a new
`source-and-evidence-map.md` (§9.4, below); and limitations, carried
forward honestly from whatever the current `README.md`'s own
"Limitations" section and `open-questions-and-conflicts.md` already
state, never invented fresh.

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

### 9.5 `codecompass-template`'s own intermediary preparation

`codecompass-template` has no `planning/knowledge/` of its own (it is a
scaffold, not a knowledge-bearing project) — its "intermediary export"
is therefore a **direct synthesis from its own real current files**
(the nine clean-room workflow templates, the optional-intermediate-
knowledge guide, `docs/architecture.md`, `docs/worked-example.md`,
`README.md`, `CLAUDE.md`), not a render from canonical records. Lighter
by construction, consistent with §11.

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
  concepts/              -- or a pointer into the already-current docs/domain/
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
finding, not a template this phase forces — `docs/domain/**` is
explicitly expected to remain, reused rather than rewritten (§7.1), and
the writer's own output integrates alongside it rather than duplicating
it.

### 12.2 `codecompass-template` — lighter, adoption-focused (§11)

A smaller tree: `README.md`, a short `docs/` (adoption + architecture +
clean-room pointer + optional-workflow pointers), no `docs/domain/`
equivalent (the template has no domain concepts of its own to document
beyond what its own README already states), no `architecture/`
directory distinct from `docs/architecture.md`.

### 12.3 Completion bar

Both repositories end with: a complete new `README.md`; a complete,
current docs tree covering real repository needs (not a mechanical
preservation of the old file list); every item in the disposition report
(§8.3) actually deleted or archived per its own recorded final action;
every internal link/navigation reference reconciled
(`check_internal_links_resolve`, re-run clean, §18); zero old and new
documentation competing side by side.

---

## 13. Cold-reader acceptance test

Before the full writer run, for each repository: a **fresh** reader
(a separate agent dispatch or a human with no prior project knowledge),
given only the Mode A branch contents (or, if Mode B is ready, the
actual isolated workspace — whichever the implementation sequence
reaches first), answers the governing request's own bounded question set
(what is this project for; main architectural components; important
interfaces; principal workflows; invariants that must be preserved; what
fails closed; configuration/testing; where a contributor would modify
X; limitations/open questions). Every question, answer, cited evidence
reference, and any "insufficient context to answer" finding is persisted
(`planning/documentation-handoff/COLD-READER-REPORT.md`). **The full
writer run does not proceed until this report shows a materially
correct project model** — a genuine gate, not a formality; a finding here
routes back to §9's own enrichment step, not forward to the writer.

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

## 15. Separation of generation and verification

The writer (generation) never has full repository/canonical access —
that is the entire point of Mode B. **Verification is a separate pass,
by a different role, with normal access restored**: `domain-skeptic`'s
existing comparison mode (already classifies
`aligned`/`partial`/`conflicting`/`not_implemented`/
`insufficiently_verified`, reused directly, no new rubric) checks the
result branch's own claims against canonical/intermediary knowledge,
source, tests, configuration, schemas, and live CLI behaviour. Findings
may be returned to a *further* writer round as bounded corrections (e.g.
"docs/reference/cli.md claims flag `--foo` defaults to `bar`; the real
default is `baz`, see `src/codecompass/cli.py:NNN`") — **never** by
revealing the old, superseded documentation to make the new output
resemble it, which would defeat the entire exercise.

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
honestly-reported tier (`verified` or `best-effort`, §6.3), actual
evidence-preparation steps, actual disposition rules applied, actual
cold-reader check results, the actual writer invocation contract, actual
verification and integration steps, deletion/archive rules as applied,
validation commands, and failure/retry behaviour observed. If reusable
scripts are written during implementation (the branch-manifest validator,
§6.1; the projection-drift checker, §10; any export/import helper), they
live under `scripts/` and are referenced by the stored document, not
left as one-off manual commands.

---

## 18. Phase 81B's own Definition of Done

Per `CLAUDE.md` §5, extended for this phase's own named deliverables:

1. Both repositories' documentation inventories complete, disposition
   reports complete and later confirmed executed against the real tree.
2. Intermediary export complete for CodeCompass (all five relevant
   slugs rendered, enrichment pass run honestly — not fabricated,
   projection-drift check passing) and the lighter template-equivalent
   synthesis.
3. Clean-room branches exist for both repositories, independently
   reviewable (Mode A), manifest-validated.
4. Mode B isolation mechanism investigated and honestly reported
   (`verified` or `best-effort`/`UNMET`, §6.3/§21) — not assumed, not
   silently upgraded.
5. Cold-reader acceptance passed for both repositories before the full
   writer run.
6. Full clean-room redocumentation actually executed and completed for
   **both** CodeCompass and `codecompass-template` — not merely
   mechanism-proven.
7. Independent, informed verification run against both results.
8. Superseded documentation given an explicit disposition and that
   disposition actually executed, confirmed against the real tree.
9. Link/navigation reconciliation clean.
10. `docs/development/clean-room-redocumentation.md` written, reflecting
    the actual proven procedure, not the original plan.
11. A per-phase docs-drift audit (`docs-reconstructor`, scoped to this
    phase's own diff) finds no misdescribing current-truth doc.
12. Learning/context-gap triage run (`knowledge-curator`); any candidate
    learning (e.g. from the isolation investigation, or from the
    overview.md-concentration root cause) triaged per the normal
    lifecycle.
13. A phase retro exists (full `TEMPLATE.md` shape, learning directly
    from this session's own prior corrective-pass experience that an
    under-filled retro costs a full extra audit round-trip).
14. An independent `release-phase-auditor` completion audit — explicitly
    inspecting: whether the writer genuinely lacked `main` access for
    whatever tier was claimed; whether Mode A/Mode B were kept distinct
    in the actual implementation, not merely in this plan's prose;
    whether both repositories' redocumentation is actually complete
    (not a partial/example run); whether every disposition-report row's
    claimed action matches the real tree; whether the stored workflow
    document is genuinely derived from what was proven, not copied from
    this plan unchanged.
15. `planning/ROADMAP.md`/`CONTEXT.md` updated to reflect the real
    outcome, including the strict-isolation backlog item's own
    resolution (§20).

Only once every condition above genuinely holds does
`planning/ROADMAP.md` mark Phase 81B `done` — the terminal action, not a
condition checked alongside the others, per `CLAUDE.md` §5's own
established sequencing.

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
closeout, §18 item 15, once the real outcome of §6.3 is known). The
backlog item's own document
(`planning/strict-isolation-for-documentation-reconstruction.md`) is
**not** rewritten now — if Phase 81B's implementation genuinely achieves
`verified` isolation for at least one real stage boundary, that backlog
item is formally resolved (closed, pointing at the new, real evidence)
as part of Phase 81B's own closeout; if it reconfirms `UNMET`/`best-effort`
a third time, the backlog item is updated with that third data point and
its own revisit trigger re-evaluated (the "whichever comes first" clause
is then fully exhausted on the "third occurrence" branch, leaving "a
genuinely separate execution substrate becomes available" as the only
remaining open trigger). Either outcome is decided by evidence Phase 81B
itself produces, not assumed here.

---

## 21. Security / isolation acceptance criteria

Direct extension of the backlog item's own already-specified criteria
(`strict-isolation-for-documentation-reconstruction.md`, "Acceptance
criteria"), reused rather than redefined:

1. At least one real stage boundary demonstrated with a mechanically-
   enforced boundary (not a curated export, not an instruction) —
   confirmed by **active** denied-access attempts, not merely passive,
   unused routes, against every one of: filesystem paths outside
   `/evidence`; parent-directory traversal; `.git` history/objects (none
   should exist at all in the Mode B workspace, §6.2); other branches;
   Git remotes; network/GitHub (including a direct attempt to resolve
   `github.com` and to search for the public CodeCompass repo by name);
   environment variables; credentials/SSH keys; MCP/connectors; and any
   agent/project shared context that might expose old documentation
   (e.g. this very conversation's own memory/context, explicitly named
   as an escape route to test — a genuinely fresh dispatch or process
   must not inherit it).
2. A real manifest (§6.1) for whatever was fed to the writer, confirmed
   sufficient by actually running the writer's own real workflow inside
   the boundary and getting a usable result — not merely confirming the
   boundary holds for an empty/trivial task.
3. For at least one of the two repositories, draft-before-reconciliation
   ordering (the fresh writer's own output exists as a committed result
   before any legacy-documentation reconciliation step runs) demonstrated
   mechanically — the reconciliation stage's own environment must not
   even contain the legacy documentation until after the draft's commit
   exists — not merely inferred from commit timestamps after the fact.
4. A written, final, four-way-separated verdict: isolation
   (`verified`/`best-effort`/`UNMET`) / workflow completion / documentation
   accuracy / coding-context usefulness (if applicable) — never collapsed
   into one overall "done."
5. Independent `release-phase-auditor` completion audit (§18 item 14).

Where a route cannot be technically prohibited in the real environment
Phase 81B actually runs in, the stored workflow document (§19) names it
explicitly as a limitation. No claim of `verified` isolation is made
anywhere (plan, retro, ROADMAP, or the stored workflow) unless every
probe and every active escape attempt in point 1 genuinely failed.

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

This plan commits to a design; three specific points are genuinely
undecided pending either explicit approval now or resolution by real
implementation evidence, named honestly rather than silently assumed:

1. **Whether to pursue the `unshare`-based isolation mechanism (§6.3) at
   all, versus accepting `best-effort` isolation upfront and spending no
   further implementation time probing it.** This plan recommends
   pursuing it once (it is a genuinely new, not-yet-tried, locally-
   available candidate, and the backlog item's own revisit trigger
   rewards finding one) but is prepared for it to fail, honestly, like
   every prior attempt.
2. **Archive location naming** (`docs/archive/` for both repositories,
   §7.3) — a reasonable default consistent with existing conventions,
   open to a different choice at approval time.
3. **Whether `architecture/historical-notes.md` is left untouched or
   folded into the new structure** (§7.2) — recommended default is
   "leave untouched," decided for real only once the clean-room writer's
   own findings exist.

None of these three blocks approval of the plan as a whole — each has a
stated, reasonable default this plan proceeds with unless the approval
response says otherwise.

---

## 24. Plan-quality self-review (performed before committing, per the governing request's own §24)

- **Does the writer truly lack access to `main`?** Only in Mode B, and
  only to whatever tier §6.3's own investigation actually proves —
  explicitly not claimed for Mode A, which this plan repeatedly labels
  as review/portability, never isolation.
- **Is branch portability confused with isolation anywhere?** No —
  §4's own lifecycle diagram and §6.1/§6.2 keep them as two named,
  distinct steps; §6's own opening principle states the distinction
  explicitly before either sub-section.
- **Does Git history remain recoverable in the writer environment?**
  Not via `git archive` (§6.2) — no `.git` directory exists in the
  output at all; a fresh, disconnected `git init` is permitted but never
  a clone/fetch from the source.
- **Could network access rediscover the public repo?** This is the
  exact, named, unresolved sub-problem of §6.3 — not claimed solved,
  flagged as implementation's own first task, with three honest possible
  outcomes stated in advance.
- **Is intermediary knowledge sufficient?** Investigated directly (§1.1)
  rather than assumed — the real concentration-in-overview.md problem is
  named with real numbers, and §9.3's enrichment step addresses the
  measured root cause (missing `assertion_kind` classification) without
  fabricating anything.
- **Are stale generated projections prevented?** §10's new check, a
  direct, scoped extension of code Phase 81 already shipped.
- **Does old documentation really disappear from the writer's search
  surface?** Only to whatever extent §6.2/§6.3's own isolation tier
  actually achieves — for Mode B `verified`, yes by construction (no old
  docs in `/evidence` at all, confirmed by the disposition-report-before-
  handoff ordering in §8.3); for `best-effort`, honestly only
  instructed, exactly as labelled.
- **Do both repositories end with complete replacement docs?** §12.3's
  own explicit completion bar, checked at audit time (§18 item 6).
- **Does every superseded doc get an explicit disposition?** §8.3's
  report format plus §16's "verified against the real tree, not merely
  trusted" requirement.
- **Are archives genuinely historical, not a dumping ground?** §7.3's
  banner requirement, navigation-path exclusion, and "exception, not
  default" framing in §7.4.
- **Is the template workflow appropriately lighter?** §11, grounded in
  §1.7's own measured current template size (no `architecture/`, no
  `docs/domain/` equivalent needed).
- **Does result import accidentally grant access back to the source
  repo?** §14 explicitly requires the orchestrator, not the writer, to
  perform the import — the writer never gains push access to anything.
- **Can another human/tool use the same handoff?** §19's tool-
  independence framing plus §6.1's Mode A review path — yes, by design.
- **Will the final proven workflow be durably stored and repeatable?**
  §17's own explicit sequencing (exercise → learn → final approved
  workflow → persist → repeat), §22 item 17.

No amendment was required as a result of this review — the plan as
drafted already addresses every point above. (Had one been required,
this section would record it rather than silently editing the plan
above without a trace, consistent with this project's own general
preference for visible, explained revision over silent rewriting.)

---

## 25. Non-implementation reminder

**This plan file, its roadmap/context updates, and nothing else, are the
only artefacts this task produces.** No clean-room branch exists. No
isolated workspace exists. No documentation has been read for disposal,
only inventoried by class in prose above. No `codecompass-template`
file has been touched. Implementation begins only on explicit approval
of this committed plan — e.g. "Approve Phase 81B and implement the
committed plan."
