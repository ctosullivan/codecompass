# Phase 79 — Clean-room conceptual understanding + documentation reconstruction (methodology hardening + template delivery)

**Status: planned, amended 2026-09-30 (second revision). Planning only —
implementation (dispatching agents, building exports, touching either
repository's real content) does not begin until this plan is reviewed
and approved.**

Direct user request, 2026-09-30, amended same day. Full initiating
prompts saved verbatim:
`planning/phase-79-clean-room-understanding-and-documentation-reconstruction-prompt.md`
(original) and
`planning/phase-79-clean-room-understanding-and-documentation-reconstruction-amendment-prompt.md`
(this revision). Governing ADR: `decisions/0066` (amended in place, same
date — see its own amendment note; not yet acted upon by any
implementation, so this is a pre-implementation correction, not a
reversal of shipped work).

**Revised objective, stated once, precisely** (replaces the first
draft's framing): *one evidence-backed knowledge foundation supplies
both coding context and project documentation, with conceptual
understanding incorporated directly into the documentation and
mechanical context separation preserved.* Understanding is no longer a
separate reviewed artifact gating publication — it is written directly
into the topic's own documentation, sourced from the same assertion
records a coding-context packet would also cite. Mechanical isolation is
tightened, not loosened: the first draft's curated-export mechanism is
demoted to *input packaging* and paired with a verified, tiered
enforcement mechanism and required preflight denial tests.

---

## 0. What changed in this revision, and why (read this first)

Six corrections, made before any implementation began:

1. **§4's separate `understanding-review.md` deliverable, its human-review
   gate, and its `review-decisions.md` correction log are removed
   entirely.** Conceptual understanding (definitions, relationships,
   rules, invariants, transformations, examples, counterexamples,
   assumptions, alternative interpretations, unresolved questions) is now
   written **directly into the topic's own published documentation**,
   with source coverage and evidence citations inline so a reader can
   audit it — never gated on a human accepting it first. This phase's own
   completion no longer depends on a human review event that may not
   occur (§5, §11).
2. **One shared knowledge foundation, not a parallel documentation-only
   store.** The existing Observation/Evidence/Claim/Derivation records
   are the single source both a coding-context packet and the published
   documentation are rendered from — restated explicitly, with a new rule
   that a documentation-time discovery must become a canonical record
   before it appears in any derived output (§4).
3. **The assertion-schema section was factually wrong and is corrected.**
   The real `Claim` status enum (verified directly against
   `scripts/check_knowledge_base.py`) is `proposed` / `supported` /
   `contradicted` / `superseded` / `verified` — not the invented
   `current`/`superseded` the first draft stated. `human_review_state` is
   removed (no field requires human review before anything). Checker
   changes are now in scope, and `check_knowledge_base.py --strict` is a
   named verification command (§4).
4. **Mechanical isolation is substantially hardened.** A curated,
   `.git`-free export is *input packaging*, not enforcement — a tool that
   can read arbitrary filesystem paths (confirmed directly: the `Read`
   tool's own description states it "is able to read all files on the
   machine") is not stopped by withholding a path from a prompt. This
   revision identifies the actually-available enforcement tiers, requires
   a live preflight denial test before trusting either one, names
   concrete indirect-leakage vectors found by direct inspection of this
   environment (including a confirmed one: `codecompass` is an editable
   install that resolves to the real checkout regardless of an isolated
   dispatch's own working directory), and requires an honest "best-effort"
   label whenever true enforcement cannot be confirmed (§6).
5. **Staged writing is clarified**: a fresh, isolated documentation
   dispatch selects the documentation architecture itself (not a
   lead-authored outline), and the hardened route is now the *default*
   ground-up documentation path — a missing prerequisite blocks that
   route rather than silently falling back to `docs-reconstructor`'s old,
   unrestricted MODE 2 behaviour. The reconciled result is published into
   **real, active project documentation** for the validation topic, not
   left as a shadow proposal (§8).
6. **Template delivery drops the understanding-review/human-review-decision
   templates**, adds a coding-context-selection template (since coding
   packets are now a co-equal derived output), and requires a fresh
   downstream usability exercise, not just committed files (§10).

Everything not named above (the schema-reuse discipline, the
`implementation-reconstructor` role, the alignment classification, the
draft-before-reconciliation ordering, the Priority-B boundary, the
validation topic) carries forward from the first draft, corrected where
this list says so.

## 1. Verified current state (re-checked live for this revision)

- **CodeCompass HEAD:** `ce7a69e` on `main`, working tree clean before
  this commit. Phase 78 is still `planned`, twice-amended, **not
  executed** — this revision does not touch, reorder, or depend on it.
- **The real `Claim` status enum**, read directly from
  `scripts/check_knowledge_base.py::_STATUS_ENUMS["claim"]`: `{proposed,
  supported, contradicted, superseded, verified}`. `Evidence`'s own enum
  is the different `{current, superseded}` the first draft's plan
  mistakenly attributed to `Claim`.
- **The real required-field and cross-reference-resolution mechanics**,
  read directly from the same script: `_REQUIRED_FIELDS` is keyed by
  `kind`, listing *mandatory* fields only — an optional field (this
  phase's new ones) needs no entry there. `check_cross_references_resolve`
  already generically extracts any `PREFIX-FEATURE-NNN`-shaped id from
  **any** field's raw value and checks it resolves — meaning a new
  `depends_on` field citing other assertion ids is validated by this
  existing function with **zero code change**, confirmed by reading its
  implementation, not assumed.
- **A confirmed, concrete leakage vector**: `.venv/bin/pip show
  codecompass-context` reports `Location: /home/cormac/projects/
  codecompass/src` — an editable install. Running `codecompass` or
  `import codecompass` from *any* working directory, including inside an
  isolated export elsewhere on the same machine, resolves to the real
  checkout's own source, not a copy. This is exactly the "import paths"
  leakage class the amendment names, now evidenced rather than
  hypothetical (§6.4).
- **The `Agent` tool's own documented isolation options**: `isolation:
  "worktree"` creates an isolated copy of *this* repository (full
  content, not scope-restricted — confirmed insufficient by the
  amendment's own critique, since a worktree still contains everything a
  curated export was meant to exclude); `isolation: "remote"` launches
  the agent in a separate cloud environment with no shared filesystem
  ("availability is gated" — not guaranteed present in a given session).
  No other isolation primitive is documented for this tool.
- **The `Read` tool's own documented behaviour**: "Assume this tool is
  able to read all files on the machine" — stated in its own description,
  confirming that granting `Read` (or `Bash`) to a dispatched agent, full
  stop, is not scoped to any directory by the tool itself. A custom
  `.claude/agents/*.md` role's `tools:` frontmatter *does* genuinely
  enforce which **tool categories** are granted at all (e.g. omitting
  `WebFetch`/`WebSearch`/`Agent` from the list means that role structurally
  cannot call them) — a real, if partial, enforcement point distinct from
  path-scoping within a granted tool.
- **Phase 78, `decisions/0060`, `docs/domain/`'s frontmatter convention,
  `codecompass-template`'s 13-file structure, and Priority A/B/D's own
  boundaries** are unchanged from the first draft's own verified state
  (`planning/phase-79-...md`'s prior version, git history) — not
  re-derived here.

## 2. Problem statement (updated)

CodeCompass's Domain/blank-slate-reconstruction mechanism (Phases
63D/64/65) produces real, useful output but has never mechanically
enforced the isolation it is only prompt-instructed to keep, has never
produced an independent, model-blind implementation reconstruction
checked against the conceptual model in both directions, and stores its
domain-concept evidence in a record shape with no field distinguishing
evidence-support from human review — and, this revision's own added
finding, no field structure suited to being *the* source both a coding
packet and a documentation page render from, since the first draft
layered a separate "review packet" artifact on top instead of publishing
the understanding directly.

This phase closes those gaps by extending the existing record shape (now
with the *correct* status enum), publishing conceptual understanding as
real documentation rather than a gated intermediate artifact, hardening
isolation to an actually-verified mechanism rather than an unverified
one, and proving the whole chain once, on one bounded topic, with the
result published into real project documentation — not a permanent
shadow proposal.

## 3. Goals, non-goals, and the Priority B distinction

**Goals:**

1. Extend the existing Claim record shape with the fields needed to
   carry a stable-ID, kind-classified, evidence-and-basis-labelled,
   dependency-aware assertion with a qualitative evidence-support state —
   using the *real* status enum, with no human-review field (§4).
2. Publish conceptual understanding directly into the topic's own
   documentation — definitions, relationships, rules, invariants,
   transformations, examples, counterexamples, assumptions, alternative
   interpretations, unresolved questions, source coverage, and evidence
   references — with no publication gate on human acceptance, while
   preserving (not requiring) any existing page-level review metadata
   convention (§5).
3. Keep one shared knowledge foundation: the same assertion records
   render both a task-specific coding-context packet and the topic-level
   documentation; a documentation-time discovery updates the canonical
   record before appearing anywhere derived (§4).
4. Identify, verify, and use an actually-effective isolation mechanism
   (not merely undisclosed paths) for four evidence scopes, with a
   required preflight denial test, an indirect-leakage checklist, and an
   honest best-effort label when true enforcement cannot be confirmed
   (§6).
5. Independently reconstruct the as-built implementation, model-blind and
   legacy-blind, freeze it, then classify alignment against the published
   understanding in both directions without forcing agreement (§7).
6. Stage documentation writing so a fresh, isolated dispatch selects the
   architecture and drafts the complete first version before any legacy
   narrative is consulted; publish the reconciled result into real,
   active project documentation for the topic (§8).
7. Add minimal, file-based, `grep`-driven propagation covering transitive
   assertion dependencies and both derived-output kinds (coding packets
   and docs), distinguishing "needs reassessment" from "proven incorrect,"
   demonstrated with one explicitly labelled controlled correction — no
   real human correction required for this demonstration (§9).
8. Deliver portable, CodeCompass-agnostic templates (dropping the removed
   review-gate templates, adding a coding-context-selection template) to
   `codecompass-template`, verified by a fresh downstream usability
   exercise (§10).

**Non-goals (unchanged from the first draft, restated):**

- No `src/codecompass/` change, no `context-graph.db` schema change, no
  new database, no graph subsystem, no comprehensive ontology.
- No re-application of the hardened workflow to the whole `docs/domain/`
  corpus or the whole `planning/v1-docs-reconstruction/` proposal — one
  topic, proven once.
- No change to Phase 78's own scope, ordering, or execution.
- No numerical confidence scores anywhere in the schema or the published
  documentation.
- No expansion into Priority B's own future runtime capability (§3's own
  closing note, below).

**This is not Priority B**, restated precisely: Priority B
(`decisions/0062`) is a future, not-yet-planned `src/`-level capability
letting a *downstream user* record and query claims about *their own*
project through the shipped tool at runtime. This phase makes zero
`src/` changes; it publishes planning artifacts, `docs/domain/` and
`docs/`/`architecture/` pages, agent briefs, and `codecompass-template`
files. It hardens and self-applies CodeCompass's own development
methodology and delivers a Priority D template artifact; it is evidence
toward Priority B's eventual planning, never that planning itself.

## 4. Assertion record schema (corrected)

No new record kind. `Observation`/`Evidence`/`Derivation` are unchanged.
The **real** `Claim` status enum, verified against
`scripts/check_knowledge_base.py`, is kept exactly as-is:

```
proposed → supported | contradicted → verified → superseded
```

(`proposed`: not yet evidenced either way; `supported`: evidence backs
it; `contradicted`: evidence conflicts with it; `verified`: confirmed
against implementation evidence specifically, the natural home for a
`domain-skeptic` alignment finding of `aligned`; `superseded`: replaced
by a newer record.) **This phase does not add, rename, or reinterpret
any of these five values.**

A Claim record used as a project-understanding **assertion** gains these
optional fields — present only when relevant, absent for an ordinary
feature-scoped Claim, so no existing
`planning/knowledge/codecompass-domain/*.yaml` file needs migrating:

| Field | Values / shape | Validation | Purpose |
|---|---|---|---|
| `assertion_kind` | `definition` \| `relationship` \| `rule` \| `invariant` \| `state_transformation` \| `boundary` | New closed-enum check, when present (§4.1) | What kind of statement this is. |
| `basis` | `directly_stated` \| `inferred` \| `proposed_policy` \| `observed_behaviour` | New closed-enum check, when present | How the statement was arrived at — structural form of `development-methodology.md`'s existing intent/behaviour/decision/meaning/uncertainty distinction. |
| `examples` | list of short strings/citations | Presence-optional, no enum | Concrete illustrating cases. |
| `counterexamples` | list of short strings/citations | Presence-optional, no enum | Cases that test or bound the assertion; an empty list means "none found," not "not considered." |
| `depends_on` | list of assertion ids | **Already validated by the existing `check_cross_references_resolve`** — no new code needed, confirmed by reading its implementation | Explicit dependency edges between assertions, for transitive propagation (§9). |
| `open_questions` | list of short strings | Presence-optional, no enum | Genuinely unresolved matters — distinct from `contradicting_evidence` (evidence exists and conflicts) and from an ordinary gap. |
| `evidence_support_state` | `supported` \| `partially_supported` \| `unsupported` \| `conflicting` | New closed-enum check, when present | A **qualitative** read of how completely the evidence backs the statement — a second, finer-grained signal alongside the mandatory `status` field, never a number. |

**No `human_review_state` field.** There is no per-assertion field
tracking whether a human has looked at it — publication and phase
completion never depend on one (§5). Any existing page-level review
metadata (`docs/domain/concepts/*.md`'s own frontmatter, `status:
APPROVED (date, reviewer)`, established at Phase 63D) is **preserved
where it already exists and is not required by this phase** — this
phase's own new content does not carry, and is not blocked by, that
convention. This does not relax the repository's ordinary planning/ADR
review conventions (`CLAUDE.md` §0/§1/§2) — those are untouched.

**No numerical confidence score anywhere** — `evidence_support_state` is
a closed, small enum, never a number.

**Versioning discipline**: a changed *statement* requires a new Claim
record whose `supersedes` field names the prior one (the existing
Domain-stage mechanism — unchanged); the prior record's own `status`
moves to `superseded`. A **withdrawn** assertion (evidence now
contradicts it, and nothing replaces it) needs no invented successor —
its own `status` simply moves to `contradicted`; `supersedes` is a field
on a *replacement* record, never a requirement that one be manufactured
just to close out a withdrawal. Every prior version stays on disk,
permanently citable — this is what makes an **immutable knowledge
snapshot** (§8's published documentation always names the exact
assertion-id-and-version set it was built from) meaningful as a citation
target.

### 4.1 One shared foundation, two derived outputs

**These records are the single knowledge foundation** — not a
documentation-only store separate from whatever a coding-context packet
(Phase 54c's existing `knowledge-curator` packet-assembly mode,
unchanged) would cite. A task-specific coding packet and the topic-level
documentation (§5, §8) are two different *renderings* of the same
assertion ids and versions, never two independently-maintained
descriptions of the same subject matter. Concretely: **a discovery made
while writing documentation, doing implementation reconstruction, or
reconciling legacy material must first become a canonical Observation/
Evidence/Claim record** (following the ordinary Domain-stage process,
`context-researcher` or a follow-up derivation) **before** it is
reflected in any derived output — a documentation page is never edited
directly with a new fact that has no corresponding record, and a coding
packet never cites a fact that only exists in documentation prose.
**Documentation prose is never itself evidence for a claim** — every
assertion's real evidence traces back through its `supporting_evidence`
to an original source (code, test, ADR, observed behaviour), never
circularly to "the documentation already says this."

### 4.2 Checker changes (in implementation scope)

`scripts/check_knowledge_base.py` gains one new, small, closed-enum
validator, shaped exactly like the existing `check_status_enums`:

```python
_OPTIONAL_ENUM_FIELDS: dict[str, dict[str, set[str]]] = {
    "claim": {
        "assertion_kind": {
            "definition", "relationship", "rule", "invariant",
            "state_transformation", "boundary",
        },
        "basis": {
            "directly_stated", "inferred", "proposed_policy",
            "observed_behaviour",
        },
        "evidence_support_state": {
            "supported", "partially_supported", "unsupported", "conflicting",
        },
    },
}


def check_optional_enum_fields(feature_dir: Path) -> list[Finding]:
    """Any of the fields in _OPTIONAL_ENUM_FIELDS, if present at all,
    must use one of its own closed values — absence is always fine
    (these fields are optional), a present-but-wrong value is not."""
```

— registered alongside the existing checks in `CHECKS`. No change to
`_REQUIRED_FIELDS` (these fields stay optional) and no change to
`check_cross_references_resolve` (already generic enough for
`depends_on`, verified in §1). **`python3 scripts/check_knowledge_base.py
--strict` is a named Definition-of-Done verification command (§11),
covering this new check the same way it already covers every existing
one.**

## 5. Understanding as published documentation, not a gated artifact

**The separate `understanding-review.md` deliverable, its human-review
gate, and its `review-decisions.md` correction log from the first draft
are removed in full.** There is no intermediate packet a human must
accept before anything is published.

`context-researcher` produces the assertion records (§4) under
`planning/knowledge/<topic-slug>/`, exactly as before. `domain-skeptic`
still adversarially reviews them before anything is published — this
step is **retained**, because it is an agent-level quality check
(unsupported claims, internal contradictions, missing counterexamples),
not a human-approval gate; its findings are resolved with further
evidence or recorded as genuine `open_questions`, never silently
smoothed over.

**What was `understanding-review.md`'s own required content is now
required content of the published topic documentation itself** (§8):
topic scope and source coverage; concepts and relationships in plain
language; rules, boundaries, exceptions, and transformations; worked
examples that test the interpretation; alternative interpretations and
unresolved questions (from each assertion's own `open_questions`); and
an evidence appendix mapping every material statement to its assertion
id and source citation — so a reader can audit the understanding directly
from the page, without a separate packet or a raw record dump. A diagram
is used only where it clarifies a relationship the prose already states.

**Publication does not require human acceptance.** A published page may
carry `open_questions` and `evidence_support_state: partially_supported`
entries openly — genuine uncertainty is disclosed in the document itself,
not hidden behind a review gate that might never resolve it. **This does
not replace this repository's ordinary planning/execution governance**:
the plan file itself still goes through the usual review this session's
own workflow already requires (`CLAUDE.md` §1), and a genuine domain
ambiguity `domain-skeptic` cannot resolve with evidence is still recorded
honestly as `open_questions` for whoever next has standing to rule on it
— it is simply no longer this phase's own blocking completion condition.

## 6. Mechanical isolation — verified enforcement, not undisclosed packaging

**Correction, stated once, precisely**: a curated, `.git`-free export
with an undisclosed source path is *input packaging* — it controls what
content a dispatch is given to work with, and reduces the odds of
*accidental* contamination, but it does **not** prevent a tool capable of
arbitrary filesystem access from *deliberately or incidentally* reading
excluded material. The `Read` tool's own description says exactly this:
it "is able to read all files on the machine." This section replaces the
first draft's claim that an export "is enforced by the export design
itself" with a verified, tiered mechanism.

### 6.1 What is genuinely enforceable, verified against this environment

- **Tool-category grants, via a custom `.claude/agents/*.md` role's own
  `tools:` frontmatter, are real.** A role that is not granted `WebFetch`,
  `WebSearch`, or `Agent` structurally cannot call them — confirmed by
  how every existing role in this project (`domain-skeptic`,
  `context-researcher`, etc.) is already defined this way. This is
  applied to every isolation-sensitive role in this phase (§6.5): no
  network tools, no `Agent` (which could otherwise re-delegate to a
  less-scoped session), `Write` limited to the role's own named output
  path by convention (not mechanically path-scoped, stated honestly).
- **`Agent(isolation: "remote")`, if available in the executing session**,
  launches the dispatched agent in a separate cloud environment with no
  shared filesystem — genuine isolation, not merely an undisclosed path,
  **if** its own preflight check (§6.3) confirms it. Availability is
  gated and not assumed present.
- **Not enforceable without remote isolation**: confining `Read`/`Grep`/
  `Glob`/`Bash`, once granted, to a specific directory. These tools reach
  anywhere the host OS permits, per their own documented behaviour. A
  curated export raises the cost of contamination (nothing relevant is
  conveniently present; the path isn't disclosed) but does not provide a
  hard guarantee.

### 6.2 The two-tier mechanism

**Tier 1 (preferred): `Agent(isolation: "remote")`**, seeded only with
the scope's own curated export content (uploaded/transferred to the
remote environment, never a shared mount with the main checkout).

**Tier 2 (fallback, used only if Tier 1 is unavailable or fails its own
preflight check): the curated export, on this same host, with the
narrowest tool grant each role's own job allows** (§6.5), explicitly
**not** claimed as hard-enforced — every artifact this tier produces is
labelled `isolation: best-effort` in its own manifest (§6.6), and "strict
clean-room" acceptance (§11) is explicitly left unmet for that stage
until Tier 1 becomes available or a stronger mechanism is found.

**Which tier is actually available is determined at execution time, by
the preflight check below — this plan does not assume the answer.**

### 6.3 Required preflight denial test (before trusting any stage's output)

Before any isolation-sensitive dispatch is trusted:

1. A trivial probe task is sent to the candidate mechanism (Tier 1 or
   Tier 2): "Attempt to read the file at the exact absolute path
   `<the real main checkout's README.md or similarly excluded file>` and
   report either its exact first line, or that the path could not be
   accessed."
2. **If the probe reports it could not access the path** (file not
   found, permission denied, or the environment has no such filesystem at
   all) — that mechanism is confirmed to provide a real boundary for this
   specific path; proceed, labelling the resulting stage's own manifest
   `isolation: verified` for the tier used.
3. **If the probe successfully reads the excluded path** — that mechanism
   provides no real boundary for this dispatch. Tier 1 failing its own
   probe means Tier 2 is used instead (still requiring its own probe,
   step 1 again); Tier 2 failing its own probe means **no stage using
   that specific tool configuration may be labelled anything but
   `isolation: best-effort`**, and every such stage's own output is
   flagged accordingly in the Definition of Done (§11).
4. The probe's own transcript (the exact prompt, the exact response) is
   persisted alongside the stage's manifest (§6.6) — not merely asserted
   to have been run.

### 6.4 Indirect-leakage checklist (checked before trusting an export)

Beyond the direct-read boundary, each export is checked for:

- **Databases**: a `context-graph.db` normally embeds narrative document
  content (`doc_artifacts`/`doc_relations_edges` rows populated from
  `README.md`/`docs/`/`architecture/` by an ordinary `sync`). **The
  Implementation-reconstruction export excludes `context-graph.db`
  entirely** for exactly this reason — a synced database is not "source,
  tests, schema, config," it is a derived index that structurally
  contains the excluded narrative. If runtime observation of a synced
  database is genuinely needed, a database built from a sync run with
  spec-doc detection disabled (or run only against the topic's own
  `src/`/`tests/` with no `docs/`-glob-matching content present at all) is
  used instead, and this substitution is stated explicitly in that
  export's own manifest.
- **Symlinks**: export construction copies real file content
  (dereferencing symlinks — e.g. `cp -rL`/`rsync -L`, never a mode that
  preserves a symlink whose target resolves outside the export root).
- **Caches**: `__pycache__/`, `.pytest_cache/`, `.ruff_cache/`, and
  `vendor/` (a generated digest that can itself embed narrative-derived
  enrichment text) are excluded from every export.
- **Import paths — a confirmed, not hypothetical, risk this environment
  actually has**: `codecompass` is installed editable
  (`.venv/bin/pip show codecompass-context` → `Location:
  /home/cormac/projects/codecompass/src`), so running the real
  `codecompass` CLI or `import codecompass` from *inside* an export
  resolves to the **real checkout's own source**, not a copy, regardless
  of the export's own content or working directory. Any dispatch that
  needs to run `codecompass` for real behaviour observation is told this
  explicitly (it is observing genuine current behaviour, which is a
  legitimate evidence type) and is separately instructed not to introspect
  the resolved module's own file path (`codecompass.__file__`, `pip show`,
  `which codecompass`) — a residual risk this project's own tooling
  cannot fully close without Tier 1 isolation, disclosed here rather than
  ignored.
- **Auto-loaded instructions**: the real project's own `CLAUDE.md`
  narrates project history/governance and must never be present in an
  isolation-sensitive export's own working directory (Claude Code
  auto-loads a `CLAUDE.md` it finds). Each export's own bootstrap (§6.7)
  supplies a minimal, purpose-written, reviewed instruction file instead
  — never the real one, never a copy of it.
- **Inherited context**: any dispatch for an isolation-sensitive stage
  uses a **fresh** agent, never `subagent_type: "fork"` — a fork
  explicitly inherits the dispatching session's *entire* conversation
  context, which already contains full knowledge of every excluded
  narrative document. The lead itself never performs an isolation-sensitive
  stage's own work directly, for the same reason.

### 6.5 Scope coverage table (unchanged shape, tightened enforcement column)

| Scope | Permitted inputs | Explicitly excluded | Tool grant |
|---|---|---|---|
| **Understanding reconstruction** (`context-researcher`) | `decisions/*.md` relevant to the topic; the relevant phase plan's own Scope/Decision sections (manifest-labelled intent/rationale, never behaviour proof); `src/codecompass/`/`tests/` for the topic; existing `docs/domain/` pages only if named explicitly | `README.md`, `docs/` outside `docs/domain/`, `architecture/`, `ai-docs/`, `CHANGELOG.md`, prior retro narrative, any unsupported inherited summary | Read, Grep, Glob, Bash (no network, no `Agent`), Write scoped to `planning/knowledge/<topic-slug>/**` |
| **Implementation reconstruction** (`implementation-reconstructor`) | `src/codecompass/`/`tests/` (topic-relevant), the relevant `graph.py` schema fragment, `pyproject.toml`, `vendor.toml` schema, CI/build config, real command output (with the §6.4 editable-install caveat) | All narrative documentation, all ADRs, the published Understanding documentation (§5) itself, `context-graph.db` (§6.4) | Read, Grep, Glob, Bash (no network, no `Agent`), Write scoped to its own report only |
| **Documentation architecture + writing** (`docs-reconstructor`, extended) | The published Understanding documentation (§5) + its cited assertion ids; the Implementation-reconstruction report + alignment classification (§7); no lead-authored outline — the dispatch selects its own structure (§8.1) | All legacy narrative documentation, unconditionally, until §8.3 | Read, Grep, Glob (no Bash needed for this role), no network, no `Agent`, Write scoped to its own draft location |
| **Documentation-only answering** (fresh `general-purpose`) | The final, post-reconciliation documentation tree for the topic only | Everything else: `src/`, tests, other docs, this project's own planning tree | Read, Grep, Glob only — no Bash, no network, no `Agent` |
| **Legacy reconciliation** (`docs-maintainer` + lead) | Everything from the writing scope, **plus** legacy narrative documentation, released only now | Nothing withheld — correct, since the clean-room draft it compares against is already committed and immutable at this point | Full, as `docs-maintainer` already has |

### 6.6 Persisted per-dispatch (under `planning/knowledge/<topic-slug>/isolation/`)

- `<scope>.manifest` — the exact allow-list, source revisions, and which
  tier (1 or 2) and label (`verified`/`best-effort`) applied.
- `<scope>.preflight.md` — the §6.3 probe's own exact prompt and
  response.
- `<scope>.access-log.md` — the dispatched agent's own observable
  research trace (reusing Phase 78's own §5.3.4 convention verbatim).
- `<scope>.boundary-check.md` — the export's own file listing checked
  against its manifest (nothing extra present).

### 6.7 Minimal reviewed bootstrap

Each export's own working directory contains, at most: the permitted
content (§6.5), a purpose-written `TASK.md` stating only the neutral task
instruction (what to investigate/reconstruct/write, with no narrative
about *why* beyond what the permitted content itself justifies), and,
where the role's own operation genuinely requires it, a minimal
`CLAUDE.md` containing only tool-usage mechanics (e.g. "run tests with
X") — never project history, governance, or narrative. This bootstrap
file is reviewed (read by the lead) before first use, exactly once per
scope, not re-authored per dispatch.

### 6.8 Breach protocol (unchanged in substance)

A boundary-check finding an unlisted file, a preflight probe unexpectedly
succeeding on a Tier the manifest already labelled `verified`, or an
access-log naming an out-of-scope path voids that stage's own output.
The export is rebuilt, a fresh agent re-runs the stage, and the breach
itself is recorded, not silently absorbed. **No stage is ever labelled
`clean-room` (as opposed to `best-effort`) after a detected breach,
retroactively rationalized as harmless.**

## 7. Independent implementation reconstruction and comparison (unchanged in substance, cross-referenced)

### 7.1 `implementation-reconstructor` (new role)

Unchanged charter from the first draft: given only the Implementation-
reconstruction export (§6.5), recovers modules, APIs/CLI, data/
persistence, dependencies, runtime paths, extension points, build/
config, tests, and limitations — `planning/knowledge/<topic-slug>/
implementation-reconstruction.md` — with no access to the published
Understanding documentation at this stage.

### 7.2 Comparison — extends `domain-skeptic`

Once the as-built report is frozen (committed), a **fresh** `domain-
skeptic` dispatch (not the instance that reviewed the Understanding
assertions) receives both the published Understanding documentation and
the frozen as-built report, and classifies every relevant behaviour:
`aligned` / `partial` / `conflicting` / `not_implemented` /
`insufficiently_verified`. Neither side is revised to force agreement. A
`conflicting` or `not_implemented` finding becomes a new `open_questions`
entry on the relevant assertion and a flagged section in the
documentation-architecture stage's own output (§8.1) — it does not
retroactively edit the already-published documentation or the frozen
as-built report; a correction, if warranted, goes through the ordinary
versioning discipline (§4, §9).

An `aligned` classification is a legitimate basis for moving the
underlying Claim's own `status` to `verified` (§4's real enum) — the
natural, already-existing status value for "evidence-confirmed against
implementation," reused rather than duplicated by a second field.

## 8. Staged documentation writing, publication, and legacy reconciliation

### 8.1 Documentation architecture — selected by a fresh, isolated dispatch, not the lead

**Correction from the first draft**: the documentation-architecture
outline is no longer a lead-authored pre-step. A fresh, isolated
`docs-reconstructor` dispatch, given the Documentation-writing export
(§6.5), opens its own output by stating the information architecture it
selects (arc42/C4-inspired views and Diátaxis-style categories, used
selectively, only where they clarify — never adopted wholesale as a
mandatory template) and why, **then** writes the complete draft under
that structure in the same dispatch. This keeps "a fresh isolated
documentation architect selects structure" a property of the dispatched
agent, not an added role.

### 8.2 Clean-room first draft

The same dispatch produces the complete first draft, distinguishing
domain concepts (citing the published Understanding documentation's own
assertion ids), project policies (citing the relevant Decision/ADR,
labelled intent/rationale), supported behaviour (citing the alignment
report's `aligned`/`partial` findings), and future intentions (citing
`not_implemented` findings explicitly as such). **This draft is committed
to `main`, under `planning/v1-docs-reconstruction/<topic-slug>/`, before
the next step begins** — the mechanical ordering gate (§11).

### 8.3 Legacy reconciliation — only after the draft is preserved

`docs-maintainer` + the lead (Phase 65's own precedent, no new role), now
with full access to both the preserved draft and the legacy narrative,
classify every relevant historical claim: `supported` /
`stale_or_contradicted` / `rationale_requiring_verification` /
`useful_example` / `obsolete` — unchanged from the first draft. Any
legacy claim folded in is re-grounded in cited evidence at the point of
incorporation; "it was already in the old docs" is never itself the
citation. Output: `planning/v1-docs-reconstruction/<topic-slug>/
reconciliation.md`.

### 8.4 Publication into real, active project documentation

**New in this revision, per the revised objective**: once reconciliation
is complete, the reconciled result is **published into the real,
currently-active documentation tree** for the validation topic — not
left as a permanent shadow proposal. Concretely, for the proposed topic
(§13): a new or extended `docs/domain/concepts/<topic-slug>.md` (the
conceptual content — definitions/relationships/rules/invariants/
examples/counterexamples/open-questions, §5) and the corresponding
updates to `docs/cli-reference.md`, `architecture/context-graph-schema.md`,
and `README.md` (the implementation-behaviour content, superseding the
existing Phase-77-authored prose on this specific topic only). This is a
real `docs/`/`docs/domain/`/`architecture/` change, still zero `src/
codecompass/` change, still not a Priority B runtime capability.

### 8.5 This is now the default route; a missing prerequisite blocks, it does not silently fall back

**Correction from the first draft**: for any future topic, this hardened
route (Understanding → Implementation reconstruction → comparison →
staged writing → reconciliation → publication) is `docs-reconstructor`'s
**default** ground-up documentation path from this phase forward. If a
topic's own Understanding snapshot or Implementation-reconstruction
report does not yet exist, that is a **named blocker** requiring those
stages to be run first — `docs-reconstructor`'s own old, unrestricted
MODE 2 behaviour (full read access, prompt-only isolation) is **retired
by this phase**, not left as a silent fallback for whenever the new
prerequisites happen to be missing.

### 8.6 Documentation-only answering and independent verification

**Tightened per this revision**: the question set is written and frozen
**before** any answering dispatch — never adjusted after seeing draft
quality. A fresh `general-purpose` agent (Documentation-only-answering
scope, §6.5) answers the frozen questions using only the final,
published documentation tree. `context-evaluator` (reused, unchanged)
independently verifies each preserved answer against real repository
evidence: correct / unsupported claim / missing information / ambiguous.
**New in this revision**: any finding of a material incorrect or
unsupported claim is **fixed in the published documentation itself**
(a normal `docs-maintainer` correction, going through the ordinary
versioning discipline, §4/§9) — verification that stops at recording a
problem without closing it is incomplete.

## 9. Change propagation (minimal, file-based, corrected for two output kinds)

No new dependency database. The traversal, run whenever a source change
affects an assertion:

```
changed source → Evidence → Claim/assertion → dependent assertions (via depends_on, transitively)
                                                        │
                                        ┌───────────────┴───────────────┐
                                        ▼                                ▼
                              cited coding-context packets      cited documentation pages
                              (planning/knowledge/*/context-packet.md)   (docs/, docs/domain/)
```

1. **Direct citers**: `grep` for the assertion id across
   `planning/knowledge/**`, `docs/domain/**`, `docs/**`, `architecture/**`,
   and any `design.md`/`context-packet.md` — the existing citation
   mechanism, no new index.
2. **Transitive citers**: any assertion whose own `depends_on` names the
   changed one, walked recursively (a handful of `grep` passes over
   `depends_on:` lines — genuinely minimal, no graph library, no
   database) — then step 1 repeated for each of those.
3. A **propagation-delta** note is written at the point of correction
   (`planning/knowledge/<topic-slug>/propagation-deltas.md`, append-in-
   place, `context-gaps/inbox.md`'s own convention): old assertion id →
   new assertion id (if superseded, per §4's versioning discipline), what
   evidence changed, why, and the full list of direct-plus-transitive
   citers found above.
4. **"Needs reassessment" vs. "proven incorrect," distinguished
   explicitly**: a citer is *proven incorrect* only if it asserted the
   specific thing the new evidence contradicts; every other citer in the
   list is *needs reassessment* — never silently assumed still correct.

### 9.1 Demonstration (no real human correction required)

**This phase demonstrates propagation with one explicitly labelled,
controlled correction — never presented as a real human correction or as
human approval.** A deliberate, disclosed test change (e.g. a corrected
`examples` entry, or a `status: contradicted` transition on one
assertion, chosen and labelled `CONTROLLED TEST CORRECTION — not a real
finding` in its own record) is introduced, and the propagation traversal
above is run against it, producing:

- a `propagation-deltas.md` entry naming every citer found;
- the **coding-context** side of propagation: a real or representative
  `context-packet.md` (Phase 54c's existing `knowledge-curator`
  packet-assembly mode, unchanged) that cites the affected assertion is
  shown re-flagged as `needs reassessment`;
- the **documentation** side of propagation: the published documentation
  page (§8.4) citing the same assertion is shown re-flagged the same way.

Both sides propagating from the **same** controlled change, from the
**same** underlying assertion, is the concrete evidence that one shared
knowledge foundation genuinely feeds both outputs — the revised
objective's own central claim, proven mechanically rather than asserted.

## 10. Template delivery (`codecompass-template`) — revised

Preserves the existing MIT licence and lightweight role; no
CodeCompass-specific agent roster, history, or governance requirement.

**New files** (added at implementation time):

- `planning/knowledge/assertions/TEMPLATE.md` — the shared assertion
  shape (§4's fields; the *real*, corrected status lifecycle; plain
  prose/YAML-optional — no requirement to use YAML).
- `planning/knowledge/snapshots/TEMPLATE.md` — how to name and cite an
  immutable snapshot (assertion ids + versions, source revisions) from
  both a coding packet and a documentation page.
- `docs/conceptual-documentation-guide.md` — **replaces** the removed
  understanding-review template: how to write definitions, relationships,
  rules, invariants, transformations, examples, counterexamples,
  assumptions, alternative interpretations, and unresolved questions
  *directly into project documentation*, with inline evidence citations,
  and no review-gate requirement.
- `planning/knowledge/coding-context-selection/TEMPLATE.md` — **new**:
  how to assemble a task-specific coding-context packet from the same
  assertion store the documentation cites, so both stay in sync by
  construction rather than by manual reconciliation.
- `docs/mechanical-isolation.md` — revised per §6: the two-tier mechanism,
  the preflight-denial-test procedure (concretely, in plain instructions
  a human can follow without any agent tooling: "ask the isolated
  worker to try to fetch/read something it shouldn't have, and confirm it
  can't"), the indirect-leakage checklist generalized to remove
  CodeCompass-specific paths, and the explicit **best-effort** fallback
  label + "leave strict clean-room acceptance unmet" instruction for a
  project whose tools cannot enforce isolation at all.
- `planning/knowledge/implementation-comparison/TEMPLATE.md` — the
  five-way alignment classification (unchanged from the first draft).
- `planning/knowledge/propagation/TEMPLATE.md` — the propagation-delta
  shape (§9), renamed from the first draft's "review-decisions" framing
  since there is no human-review gate to log corrections against.
- `planning/knowledge/legacy-reconciliation/TEMPLATE.md` — the five-way
  historical-claim classification (unchanged).
- `planning/knowledge/documentation-verification/TEMPLATE.md` — the
  frozen-question Q&A-and-verification shape (§8.6), including the
  "fix the finding, don't just record it" closing step.

**Removed from the first draft's plan**: `planning/knowledge/
understanding-review/TEMPLATE.md` and `planning/knowledge/
review-decisions/TEMPLATE.md` — no longer part of this workflow.

**Required, not optional**: these files are actually committed to
`codecompass-template` at implementation time (not merely described),
**and** a fresh downstream usability exercise is run — a fresh
`general-purpose` agent, given only the updated template repository (no
CodeCompass context), attempts to follow the templates for a small,
invented, non-CodeCompass scenario (e.g. "document one module of a toy
project using this workflow") and reports where the instructions were
unclear or CodeCompass-specific assumptions leaked through. Findings are
fixed before this phase's own Definition of Done is met (§11).

## 11. Definition of Done / review gates (revised — no human-blocking gate)

1. **Schema correction documented** (§4, in `development-methodology.md`
   and this plan) — mechanical.
2. **`check_knowledge_base.py`'s new optional-enum check implemented and
   passing `--strict`** (§4.2) — mechanical.
3. **Understanding assertions produced and adversarially reviewed**
   (`context-researcher` + `domain-skeptic`, §5) — mechanical/agent gate.
   **No human-acceptance gate follows this step** — publication proceeds
   once the adversarial review is satisfied, per §5's own removal of the
   human-review gate.
4. **Isolation mechanism identified, preflight-verified, and labelled
   honestly** for every scope in §6.5 (`verified` or `best-effort`,
   never asserted without its own persisted preflight transcript) — a
   named, checked condition, not an aspiration.
5. **Implementation reconstruction complete, model-blind and
   legacy-blind, no unrecovered boundary breach** (§7.1).
6. **Alignment classification complete** (§7.2), citing the published
   Understanding documentation directly (not a pre-publication draft).
7. **Documentation-architecture selection + complete first draft
   produced by a fresh, isolated dispatch, committed before
   reconciliation begins** (§8.1-8.2) — mechanical ordering gate, checked
   via `git log`.
8. **Legacy reconciliation complete, every incorporated legacy claim
   re-grounded in cited evidence** (§8.3).
9. **Reconciled result published into real, active project documentation
   for the topic** (§8.4) — this phase's own concrete, shippable output,
   not a shadow proposal.
10. **Documentation-only Q&A run against frozen questions, independently
    verified, and every material finding fixed** (§8.6) — verification
    that only records a problem, without fixing it, does not satisfy this
    gate.
11. **Propagation demonstrated with one explicitly labelled controlled
    correction, reaching both a coding-context artifact and a
    documentation page** (§9.1) — labelled as a test correction throughout,
    never presented as a real finding or human approval.
12. **Template deliverables committed to `codecompass-template` and a
    fresh downstream usability exercise run, with its findings fixed**
    (§10).
13. **Standard closeout** (`CLAUDE.md` §5, unchanged): docs drift audit,
    phase retro, learning triage, independent `release-phase-auditor`
    completion audit, terminal `roadmap-context-curator` reconciliation.

**No gate in this list requires an event only a specific named human can
perform.** Where an isolation tier cannot be verified (gate 4), the
honest outcome is a `best-effort` label recorded plainly — the phase can
still be reported done, with that limitation stated, rather than blocked
on a mechanism this project's own tools may not provide. This is a
deliberate, disclosed difference from the first draft's gate 3, which
made a real human review the phase's own load-bearing blocker; the
revised objective removes that dependency by publishing understanding
directly rather than gating it.

## 12. Files expected to change

### 12.1 This planning commit (now)

- **Rewritten:** this file; `decisions/0066-...md` (amended in place,
  with its own amendment note — not yet acted upon by any
  implementation).
- **New:** `planning/phase-79-clean-room-understanding-and-documentation-reconstruction-amendment-prompt.md`
  (this revision's own verbatim initiating prompt).
- **`planning/ROADMAP.md` / `planning/CONTEXT.md`:** updated to reflect
  the revised objective and gate structure.
- **`planning/v1-redefinition/development-methodology.md` /
  `documentation-lifecycle.md`:** amendment notes updated for the revised
  design (schema correction, no human-review gate, publication into real
  docs).

### 12.2 At implementation time — CodeCompass repository

- `.claude/agents/implementation-reconstructor.md` (new).
- `.claude/agents/domain-skeptic.md` (extended: comparison mode, §7.2 —
  unchanged from the first draft's own extension).
- `.claude/agents/docs-reconstructor.md` (MODE 2 **retired as a silent
  fallback**, replaced by the staged, isolated route as default, §8.1,
  §8.5; architecture-selection folded into its own dispatch).
- `.claude/agents/docs-maintainer.md` (extended: five-way historical-
  claim classification, §8.3; draft-before-reconciliation ordering;
  fix-not-just-record for §8.6 findings).
- **`.claude/agents/context-researcher.md`** (named explicitly per this
  revision's own instruction — its operating mode under this workflow is
  documented: dispatched into the Understanding-reconstruction export,
  §6.5, rather than its default "everything" read scope, when running
  under this hardened route specifically; its ordinary feature-scoped
  Domain charter for work *outside* this workflow is unchanged).
- `scripts/check_knowledge_base.py` (new `check_optional_enum_fields`,
  §4.2).
- `planning/v1-redefinition/agent-led-development.md` (§2.11
  `context-researcher` entry's write-boundary table row updated for this
  workflow's own scoped mode; §2.13 `domain-skeptic` extended; new §2.15
  `implementation-reconstructor` catalogue entry).
- `planning/knowledge/<topic-slug>/**` (assertion records, implementation-
  reconstruction report, alignment report, isolation manifests/preflight
  transcripts/access-logs/boundary-checks, propagation-deltas,
  documentation Q&A + verification).
- `docs/domain/concepts/<topic-slug>.md` (new or extended, §8.4).
- `docs/cli-reference.md`, `architecture/context-graph-schema.md`,
  `README.md` (updated for the topic, §8.4).
- `planning/v1-docs-reconstruction/<topic-slug>/` (staged draft +
  reconciliation report, preserved per §8.2's ordering gate).
- Standard closeout files (retro, drift-audit report, learnings, audit
  report).

### 12.3 At implementation time — `codecompass-template` repository

- The eight `TEMPLATE.md`/guide files named in §10 (replacing the first
  draft's six — two removed, two added).
- `README.md` cross-link update.

## 13. Validation topic (unchanged proposal, output scope corrected)

**Proposed, provisionally: CodeCompass's own first-party source/symbol
subsystem** (`source_files`/`source_symbols`, `Language`, `exposure`,
`symbol_index_status`, `codecompass query source`/`query source-symbol`
— Phase 77, `decisions/0065`) — confirmed real and available directly
against this repository, unchanged from the first draft's own
verification.

**Honest scoping note, restated**: this topic's knowledge-sources layer
is thin (an ADR and a phase plan's own intent sections, no external
manual) because this specific topic genuinely has none — a real,
disclosed limitation of what this pilot can prove about the *richer
external-manual* case (e.g. Ledgerkit-with-the-hledger-manual), which
`codecompass-template`'s own guidance must still support even though this
pilot does not exercise it. The mechanism itself (schema, isolation,
implementation comparison, staged writing, reconciliation, publication,
propagation) is fully exercised regardless.

**This phase's own output is a complete topic-level pilot — one
subsystem, published into real documentation — not whole-project
redocumentation.** `docs/domain/`'s remaining concepts, and
`planning/v1-docs-reconstruction/`'s own broader six-category shadow
proposal, are explicitly untouched by this phase.

## 14. Roadmap placement (unchanged)

Tracked in `planning/ROADMAP.md`'s "Post-v1 development" table as an
ordinary phase, cross-referenced from Priority D's own status cell as its
next concrete deliverable — not a new lettered priority.

## 15. Human decision gates (revised — none load-bearing)

**One real judgment call, presented for review**: the validation topic
choice (§13) — resolved by evidence, substitutable without redesign if
rejected.

**A second, genuinely open technical question, not a human-decision gate
but a real uncertainty**: whether `Agent(isolation: "remote")` is
actually available in the session that eventually executes this phase.
This plan does not assume an answer (§6.2) — the preflight check (§6.3)
decides it live, and either answer produces a valid, honestly-labelled
outcome.

**No gate in this revision requires a specific named human to act before
the phase can be reported done** — the load-bearing human-review gate
from the first draft is removed per §5/§11's own explicit correction.
Ordinary planning/ADR review (`CLAUDE.md` §0-§2) still applies to this
plan and its ADR themselves, unchanged.

## 16. Rollback / cleanup requirements (unchanged in substance)

- Every isolated export lives under the session scratchpad (Tier 2) or
  the remote environment's own disposable storage (Tier 1), never inside
  either repository's tracked tree, deleted once its stage's output is
  committed and its manifest/preflight/access-log/boundary-check are
  persisted.
- No generated CodeCompass runtime artifact is committed anywhere by this
  phase in either repository, beyond what an export genuinely needs to
  inspect (itself deleted per the above).

## 17. Verification commands

- `.venv/bin/pytest -q`
- `.venv/bin/ruff check .`
- `python3 scripts/check_user_docs.py --strict`
- `python3 scripts/check_knowledge_base.py --strict` (now a required,
  not merely available, command — §4.2's new check must pass under
  `--strict`).
- At implementation time: each scope's own `<scope>.preflight.md` and
  `<scope>.boundary-check.md` (§6.6), checked before that scope's output
  is treated as valid at any label.

## 18. Remaining technical uncertainties (stated plainly, not resolved by assertion)

1. **Whether `Agent(isolation: "remote")` will actually be available and
   working when this phase is executed** — unverifiable at planning time;
   resolved live by §6.3's own preflight check, with an honest
   `best-effort` fallback already specified either way.
2. **Whether the editable-install leak (§6.4) can be fully closed without
   Tier 1 isolation** — the disclosed mitigation (don't introspect the
   module path) reduces but does not eliminate the risk under Tier 2; a
   genuinely clean fix would need a non-editable, export-local install of
   `codecompass`, which is real additional implementation work not yet
   scoped here and would be added at implementation time if Tier 2 is the
   only available mechanism.
3. **Whether `docs-reconstructor`'s existing per-phase drift-audit mode
   (MODE 1, unaffected by this phase) needs any adjustment now that MODE
   2's default behaviour changes** — expected "no" (the two modes are
   already independent), but not exhaustively re-verified against every
   existing MODE-1 dispatch pattern in this planning pass.
