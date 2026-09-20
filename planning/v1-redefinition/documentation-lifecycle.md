# Documentation lifecycle plan (required outputs 6 and 12)

Redefines documentation management as a **lifecycle** — incremental
maintenance during development *plus* blank-slate renewal at milestones —
rather than perpetual incremental patching that accretes caveats.

Implemented by Phase 42 (incremental + closeout gate) and Phase 64–65
(blank-slate reconstruction + reconciliation; corrected here from this
document's own original "Phase 60–61" — those numbers predate the Stage
F/G +4 renumbering `decisions/0056` performed). Preceded by Phase 63D
(`decisions/0060`), which supplies the domain corpus §3 now consumes.
Owned by `docs-maintainer` (incremental) and `docs-reconstructor`
(blank-slate).

## 1. Three distinct documentation roles

### 1.1 Current truth — active documentation
`README.md`, `docs/`, `architecture/`, `ai-docs/`. Describes CodeCompass
**as it exists now**. Explicitly allowed to be substantially rewritten,
reorganised, consolidated, split, or **deleted**. It must **not** be
forced to explain every historical way CodeCompass once worked.
> Current documentation earns its place by accurately and economically
> explaining the current project.

Current visible debt this is meant to fix: `architecture/overview.md` is
**1,954 lines** and already shows the accretion pattern (historical
notes, "superseded by" pointers, "Phase N added… later Phase M changed…"
narration inline). That is decision history living in a current-truth
doc.

### 1.2 Decision history — ADRs
`decisions/`. Preserves **why** the project evolved as it did.
Append-only (`CLAUDE.md` §2). A superseded ADR stays as a historical
record — it is **not** rewritten to pretend the old decision never
happened; it gets a short addendum pointing at its successor, and the
successor states the reversal.

### 1.3 Historical milestone state — git tags / releases + closeout artifacts
Git tags/releases are the primary archive of complete historical source +
documentation state. The active repo does **not** carry full duplicate
documentation trees to preserve history. Where useful, a milestone may
add a concise closeout artifact (see §5): a closeout report, an
architecture summary, a release-doc bundle, a retired-concept note.

### 1.4 Six documentation categories, by content type (added `decisions/0060`, 2026-09-20)

Orthogonal to the freshness-based split above (§1.1–1.3), current-truth
documentation itself separates into six categories by *what kind of
content* it holds — a distinction Phase 64's own blank-slate
reconstruction now makes explicit in its own output structure:

1. **Domain** — what CodeCompass's own concepts mean (evidence,
   observation, adapter, context packet, etc.). Lives at `docs/domain/`
   (Phase 63D's own deliverable, `decisions/0060`). Answers "what is an
   adapter," never "how is `NpmAdapter` implemented."
2. **Architecture** — how those concepts are implemented. Lives at
   `architecture/`. Answers "how does `sync.py` wire an adapter into the
   graph," assuming the reader already knows what an adapter *is* (from
   §1's own domain docs).
3. **User** — how CodeCompass is used. Lives at `docs/` (CLI reference,
   config schema, quickstart).
4. **Developer** — how CodeCompass is extended (writing a new adapter,
   the test/lint/release workflow). Lives at `CONTRIBUTING.md` and
   developer-facing sections of `docs/`/`architecture/`.
5. **Protocol/adapter** — how external components integrate
   (`docs/external-adapters.md`, the external-process wire protocol,
   `decisions/0057`-`0059`).
6. **Development-process** — how Scope → Plan → Domain → Design →
   Implement itself operates (`development-methodology.md`, made
   durable and user-facing at Phase 64 rather than staying a
   `planning/v1-redefinition/`-scoped internal doc).

A single physical file may still serve more than one category
economically (e.g. `architecture/overview.md` mixing architecture and
some protocol/adapter content is fine) — the point of naming these six
is to make sure Phase 64's own reconstruction *considers* each
category deliberately, not that every category needs its own
dedicated file from day one.

## 2. Incremental maintenance during development (the everyday half)

On any phase that changes CLI behaviour, config schema, generated-file
formats, or system design:

1. The implementing work updates affected `docs/` / `architecture/` /
   `README.md` / `ai-docs/` **in the same commit** (`CLAUDE.md` §2 —
   unchanged).
2. `docs-maintainer` then reconciles: checks the doc change against the
   **verified** implementation (not the plan's intent); rewrites weak
   prose; **removes** now-false statements; **resists** adding "note:
   since Phase N this also…" — if a paragraph is now wrong, fix the
   paragraph, don't annotate it.
3. Deterministic doc checks run (`scripts/check_user_docs.py`, extended
   in Phase 42): every CLI command documented; README phase/feature
   claims consistent with `ROADMAP.md`; every `VendorConfig`/schema field
   documented; `ai-docs/` files present and non-empty; **internal links
   resolve; fenced example commands are real commands** (new in Phase 42).
4. **`docs-reconstructor` runs the per-phase drift audit** (§2.5).
5. `release-phase-auditor` (or lead) confirms as part of DoD.

Goal of this half: **keep current documentation accurate during
development.** It is only half.

## 2.5 Per-phase independent docs-drift audit (`CLAUDE.md` §5 DoD condition)

Step 2 above has a gap: `docs-maintainer` both edits the docs and
certifies them accurate — nothing independent checks that. Every phase
therefore also gets a **read-only drift audit by `docs-reconstructor`**
(the independent agent), added to `CLAUDE.md` §5 at the user's request
(2026-09-10):

- **Input:** the phase's actual diff — not `docs-maintainer`'s summary of
  what it changed.
- **Scope:** what actually changed about *observable* system behaviour
  (CLI, flags, config schema, generated-file formats, defaults,
  user-visible errors, module responsibilities). Pure internal refactors
  with no observable change implicate no docs.
- **Method:** for each such change, `grep` the current-truth docs
  (`README.md`, `docs/`, `architecture/`, `ai-docs/`) for the affected
  command/flag/symbol/concept and check every hit against the **verified**
  new behaviour (read the code / run `--help`).
- **Verdict:** `NO DRIFT` or `DRIFT — n findings` (each: `file:line`, the
  now-false sentence, what the code does, blocking vs non-blocking).
  Findings go back to `docs-maintainer` → re-audit.
- **`NO DRIFT` is the common, expected verdict** for a phase that only
  touched `planning/`, `.claude/`, tests, or internal code. The audit is
  cheap for those (a one-line scope note) and real value on a phase that
  changed CLI surface.

This is **not** the blank-slate reconstruction (§3) — it is scoped, per
phase, and never proposes a rewrite. It is the everyday independent
counterweight; §3 is the milestone renewal.

## 3. Blank-slate reconstruction (the milestone half) — Phase 64

At major milestones, `docs-reconstructor` approaches CodeCompass **as
though the current narrative documentation did not exist** — with one
deliberate exception, added `decisions/0060` (2026-09-20): **domain
terminology is not rederived from scratch here.** Phase 63D
(`planning/phase-63d-domain-reconstruction.md`) already ran a dedicated,
evidence-backed, adversarially-reviewed investigation of CodeCompass's
own core concepts specifically, and its approved output is authoritative
for what those concepts mean — this phase consumes it rather than
guessing at terminology a prior, more careful pass already settled.

- **Inputs (authoritative project reality only):** current `src/`;
  tests; CLI behaviour / `--help`; config / schema; generated outputs
  (a real `vendor/`, a real `context-graph.db`, generated Skills,
  `/discovery`); ADRs; current `architecture/` *(read for facts, not for
  narrative structure)*; current planning/project state; **Phase 63D's
  own approved `docs/domain/` corpus** (the one deliberate exception to
  "ignore existing docs" — domain meaning, not documentation structure,
  is out of scope for re-derivation here).
- **It does not read `README.md` / `architecture/overview.md` as a
  starting structure** — the point is a fresh derivation of what a new
  user, contributor, maintainer, and AI coding agent each need, and how
  the current system should be explained from scratch.
- **Output:** a temporary/shadow proposal under
  `planning/v1-docs-reconstruction/`, organized by the six documentation
  categories (§1.4): a domain section (built from `docs/domain/`,
  reorganized for presentation if needed, not re-derived), proposed
  `architecture/` set, proposed `docs/` set (user + developer content),
  a protocol/adapter section, and a development-process section
  (`development-methodology.md`, made durable/user-facing here) — plus
  an explicit list of concepts the current docs spend words on that the
  current *system* no longer justifies.
- **It does not overwrite anything.**

## 4. Reconciliation — Phase 65

Compare, deliberately:

```
current project reality  →  blank-slate reconstruction
              VERSUS
        existing active documentation
```

For **each** current doc (and each proposed doc), a recorded decision:
**retain / rewrite / consolidate / split / replace / remove / preserve
only in historical state (tag + closeout)**.

The output is a reconciliation table
(`planning/v1-docs-reconstruction/reconciliation.md`) with a one-line
rationale per doc, then the lead + `docs-maintainer` action it. This is
what prevents:

```
old explanation + later caveat + later exception + migration note
+ correction + additional caveat = technically defensible, conceptually poor
```

Expected large item at the redefined-v1 milestone: `architecture/overview.md`
split into a lean current-state document + the historical/superseded
narration moved out (to ADR addenda where it's rationale, or simply
dropped where git history already covers it).

## 5. Milestone documentation closeout gate — Phase 69

The operational form is **`planning/milestone-closeout-checklist.md`**
(created in Phase 42) — a per-step checklist with owners and "done"
signals, executed at Phase 69. In outline:

1. deterministic documentation checks pass;
2. domain reconstruction done (Phase 63D);
3. blank-slate reconstruction done (Phase 64);
4. comparison / reconciliation done (Phase 65);
5. obsolete current documentation deleted (not annotated);
6. link / example / reference validation passes;
7. architecture documentation review — current-state only, history
   removed;
8. ADR status review — superseded ADRs marked (not rewritten); any
   decision made during the milestone that lacks an ADR gets one;
9. final current-doc freeze for the milestone (no further current-doc
   edits until after the tag, except fixes to what the freeze itself
   surfaces);
10. **phase retros for the milestone's phases reviewed in bulk** — the
    `planning/retros/` entries since the last milestone are read for
    recurring process feedback; anything actionable becomes a
    `knowledge-curator` promotion (a workflow edit, a roster change, a
    `CLAUDE.md` proposal) and is noted in the closeout artifact;
11. milestone closeout artifact written where useful
    (`planning/v1-closeout.md`: architecture summary, what shipped, what
    deferred + revisit triggers, key ADRs, reference-project evaluation
    results, distilled process lessons from the retros);
12. git tag / release preserving the complete historical state.

## 6. ADR lifecycle (unchanged mechanism, explicit here)

- New ADR whenever a phase involves a non-obvious tradeoff (`CLAUDE.md`
  §2) — including tradeoffs surfaced by reference-project evidence, not
  only ones known up front.
- Reversal → new numbered ADR + addendum on the old one. Never edit a
  past ADR's original content.
- Phase 65 step 7 is a *review*, not a rewrite — it checks that every
  superseded ADR carries its pointer and every milestone decision has a
  record.

## 7. What does not change

- `CLAUDE.md` §0 (protected-file approval) applies to `CLAUDE.md` itself
  regardless of anything here. `docs-reconstructor` and `docs-maintainer`
  never touch it.
- `CLAUDE.md` §2's same-commit rule for the *incremental* half.
- The `decisions/` append-only rule.
- `decisions/0039` (ship without a dedicated docs site) stands unless a
  Stage F finding supersedes it — the reconstruction may *recommend* a
  site if real reference-project/user friction showed up, via a new ADR.
