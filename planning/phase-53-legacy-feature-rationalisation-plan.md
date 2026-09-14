# Phase 53: Legacy feature rationalisation — plan

**Status:** planned (awaiting review gate — see "Review gate" at the end
of this file). This file is the plan; the full verbatim request is
`planning/phase-53-legacy-feature-rationalisation-prompt.md`.

Retargets the roadmap's `53–55` "Stage D — deeper Ledgerkit dogfooding"
slot's first phase to this scope, per the same findings-drive-scope
precedent Phase 49 (against 48/49) and Phase 52 (against the original
"Stage D" sketch) already established — recorded in the `ROADMAP.md` diff
alongside this plan. This does **not** resolve the open Stage
D-vs-Stage-F/G strategic decision from Phase 51's retro; it is orthogonal
to it, exactly as Phase 52 was.

## Depends on

- Phase 52 done (context-observations lifecycle + agent-driven
  enrichment — `decisions/0054`).
- No other phase. This is a self-contained architecture review of
  already-shipped code, not new capability.

## Scope

**In scope**, per the prompt's own required sections:

1. Current-state architecture summary.
2. A complete feature/subsystem inventory, classified.
3. A redundancy map.
4. A proposed target architecture (documentation-level grouping, not a
   `src/` restructuring — see "Design decisions" below).
5. Per-feature decisions with rationale and evidence.
6. Compatibility implications of whatever is approved.
7. An implementation sequence for the approved work.
8. Evaluation requirements (how we'll know a removal/narrowing didn't
   regress anything).
9. Acceptance criteria.

**Explicitly out of scope** (per the prompt): new relationship types,
embeddings/vector search, hosted infrastructure, multi-repo support, MCP
work, IDE interfaces, autonomous graph learning, a graph schema rewrite,
sophisticated ranking, any unrelated Ledgerkit feature work.

**This plan does not implement anything.** Per the prompt's explicit
"Once the Phase 53 plan has passed the normal review gate, implement the
approved rationalisation work" instruction, and per `CLAUDE.md` §1's
"if writing the plan surfaces an assumption not already settled, pause
and ask before proceeding from plan to code" — several of this plan's
live candidates are product-direction calls (removing a working,
tested, documented feature), not mechanical follow-through. Sections 5–9
below describe what *would* happen once approved; a second, narrower
implementation-phase plan (or a direct diff, for the smallest items) is
written only after the user has chosen among the options this document
lays out.

## Design decisions

- **The "target architecture" is a documentation/grouping exercise, not
  a package restructuring.** The prompt's own scope exclusions (no MCP
  work, no IDE interfaces, no graph schema rewrite) and this project's
  standing "don't refactor beyond what a task requires" rule both argue
  against moving files into new `core/`/`agent/`/`adapters/` directories
  for a boundary that can be stated equally clearly in
  `architecture/overview.md` prose plus a few module-docstring updates.
  Section 4 states the grouping; it is not a migration plan.
- **`adapters/` (the existing package) and "adapter" (the prompt's usage,
  meaning Claude Skill / CLAUDE.md / Cursor output) are two different
  senses of the same word.** `src/codecompass/adapters/` is the
  ecosystem-package-manager abstraction (`decisions/0002`: npm/Python/
  Cargo). The prompt's "ADAPTERS" tier is the *output-format* boundary
  (Claude Skills, `CLAUDE.md`, Cursor `.mdc`). This plan calls the latter
  "host-output adapters" throughout to keep the two distinct, and flags
  the naming collision itself as a (very small, doc-only) finding.
- **Evidence bar for REMOVE**: no known caller/consumer in this
  codebase's own tests or generated output, *and* no evidence of real use
  from any reference-project evaluation to date (`findings.md`,
  `context-observations/`, `context-gaps/`). A feature that is merely
  *unproven* (no positive evidence either way) is DEFER PENDING
  EVALUATION, not REMOVE — removing on absence-of-evidence alone would
  contradict this project's own "agent observation is not authoritative"
  posture (`CLAUDE.md` §8) turned outward on itself.

---

## 1. Current-state architecture

CodeCompass's runtime is 23 modules under `src/codecompass/` (7,248
lines) plus a 5-module `adapters/` sub-package (515 lines) implementing
`EcosystemAdapter` for npm/Python/Cargo (`decisions/0002`). Shape, by
pipeline stage:

**Bootstrap / discovery** — `discovery.py` (manifest parsing +
`vendor.toml` writing), `config.py` (`vendor.toml` parsing).

**Ecosystem adapters** — `adapters/{base,npm,python,cargo}.py`:
installed version, source location, README/API-surface extraction,
repository URL resolution, dependency tree. One class per ecosystem
against `EcosystemAdapter`'s abstract interface; adding an ecosystem
means writing one adapter, not touching core logic.

**Mechanical generation (Phase A, always free, no AI)** — `sync.py`
(orchestrates a vendor's full pipeline), `symbols.py`, `filetree.py`,
`deptree.py`, `usage.py` (real `(file, line)` usage-site detection),
`source_resolution.py` (pinned clone management), `claude_md.py`
(per-vendor `CLAUDE.md` template), `staleness.py` (`check` command's
staleness + coverage gate).

**Context graph** — `graph.py` (not read in full this phase, but its
schema is the join point every other module writes to or reads from:
`vendors`, `symbols`, `uses_edges`, `doc_artifacts`, `documents_edges`,
`skill_mentions_edges`, `routes_via_edges`, `depends_on_edges`,
`doc_relations_edges`, `vendor_enrichment`, `symbol_enrichment`,
`doc_relation_enrichment`).

**AI enrichment (Phase B, optional, cost-gated)** — `enrichment.py`
(vendor/symbol-level, direct Anthropic API, batched forced-tool-use),
`relation_enrichment.py` (spec-doc-relationship-level, same call
pattern, sibling not shared module per `decisions/0038`), plus Phase
52's second, non-API producer: `cli.py`'s `enrich apply` command +
`.claude/agents/context-enrichment-agent.md`, writing through the same
`relation_enrichment.apply_results` with `model=f"agent:{name}"`
(`decisions/0054`).

**Host-output generation (templated, deterministic, no AI)** — `skill.py`
(tool-level Skill unconditionally, per-vendor Skill + Cursor `.mdc` once
enriched), `commands.py` (`/discovery` slash command), `index.py`
(project-root `CLAUDE.md` routing-table injection).

**Human/agent-facing entry points** — `chat.py` (single-vendor digest
REPL, demoted to secondary by `decisions/0034`), the `query_app` CLI
subgroup (`vendors`/`vendor`/`symbol`/`skills`/`relations`), `/discovery`
(above), and the generated Skills/routing table themselves.

**CLI surface** (`cli.py`, 6 top-level commands, 5 `query` subcommands, 1
`enrich` subcommand): `init`, `sync`, `index`, `check`, `chat`, `undo` +
`query {vendors,vendor,symbol,skills,relations}` + `enrich apply`.

Three real, distinct consumers of `import anthropic` exist:
`enrichment.py`, `relation_enrichment.py`, `chat.py`. `anthropic>=0.109`
is a hard, pinned runtime dependency in `pyproject.toml` — no optional-
extras mechanism isolates it from the deterministic path today.

Three parallel planning-queue mechanisms exist for capturing
non-code-review feedback about CodeCompass's own output:
`planning/context-gaps/` (missing/requested edges, `decisions/0051`),
`planning/context-observations/` (experience with edges that already
exist, Phase 52), `planning/learnings/` (process learnings). All three
are triaged by `knowledge-curator` (`.claude/agents/knowledge-curator.md`).

## 2. Feature inventory

| # | Feature | Purpose | Original rationale | Current implementation | Callers / users | Evidence of real usefulness | Owner | Overlaps with | Maintenance burden | Class | Recommended action |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Vendor/symbol direct-API enrichment | Grounded technical description, conversational overview, per-symbol purposes for usage-proven vendors | `decisions/0031` — usage-driven, not depth-gated | `enrichment.py` (621 lines), wired via `cli.py::_maybe_run_enrichment` | `sync`/bare `codecompass`; read by `claude_md.py`, `skill.py`, `chat.py` | This repo's own `vendor/*/CLAUDE.md` (self-dogfood only); **zero evidence from any reference-project evaluation** — `findings.md` never exercises this path (Ledgerkit isn't a tracked vendor of CodeCompass's own project) | Lead (`src/`) | Relation enrichment (same call shape); Phase 52's agent-driven path (same *purpose*, different mechanism, currently only for relation-level) | High — 621 lines, batching, hashing, a forced-tool-use schema, its own error type | REQUIRES EVALUATION | See §5.1 |
| 2 | Relation (spec-doc) direct-API enrichment | AI-summarised *how* a mechanically-detected doc↔dependency/Skill relation relates | `decisions/0038` (non-negotiable: never writes spec docs) | `relation_enrichment.py` (574 lines) | `_maybe_run_enrichment`; read by `query relations` | Same call shape now has a **proven, live-demonstrated alternative** (Phase 52) that needed zero `ANTHROPIC_API_KEY` | Lead | Feature 1 (shared batching/hashing pattern); Feature 3 (identical output table, different producer) | Medium-high — 574 lines | REQUIRES EVALUATION | See §5.1 |
| 3 | Agent-driven relation enrichment | Same output as #2, produced by a Claude Code agent's own reasoning instead of a billed API call | `decisions/0054`, Phase 52, direct user request (no API key in this dev environment) | `cli.py::enrich_app.apply` + `.claude/agents/context-enrichment-agent.md` | Dispatched manually by the lead today; not yet auto-triggered by any command | **Live-demonstrated twice** (`tests/fixtures/ledgerkit_lifecycle_demo/DEMO.md`), correctly rejected a stale resubmission | Lead + curator role | Feature 2 | Low — one CLI command + one agent brief, reuses existing validation | CORE (new, adjacent) | KEEP — see §5.1 for whether it should *replace or sit alongside* #2 |
| 4 | Chat REPL | Digest-only Q&A for one vendor | `decisions/0012` (original "the actual product") | `chat.py` (132 lines) | `codecompass chat <vendor>` | `decisions/0034` already demoted this to secondary; **zero evidence of use** in any of the 5 evaluated Ledgerkit instances (`findings.md`) — all evidence is `query`/graph-based | Lead | None structurally; conceptually overlaps with `query vendor`'s job of "tell me about this vendor" | Low — small, self-contained, third-party-API-only | REQUIRES EVALUATION | See §5.2 |
| 5 | "Initial-chat" / project-root entry point / whole-project rollup | (as named in the prompt) a project-level conversational entry point | Sketched, never built — Post-MVP Phase 20/24 (`decisions/0048`: deferred) | **Does not exist.** `chat.py`'s own docstring: "Explicit-vendor mode only; project-root routing and the whole-project rollup are post-MVP Phase 20." Two grep hits total across the repo, both describing the undelivered concept | n/a | n/a — never shipped | n/a | n/a | None — nothing to remove | DEPRECATED-BY-NEVER-EXISTING | No action — see §5.3 |
| 6 | Tool-level Skill | Mechanical signal that CodeCompass exists + how to query it | `decisions/0020` — unconditional, regardless of vendor count/enrichment | `skill.py::render_tool_skill/write_tool_skill` | Generated into `.claude/skills/codecompass/SKILL.md` on every `index`/sync | Real — this is the artifact every Claude Code session in a CodeCompass-tracked project actually loads | Lead | `/discovery` (near-identical command list prose, see §3); root `CLAUDE.md` routing table (also lists vendors) | Low-medium | ADAPTER (host-output) | KEEP |
| 7 | Per-vendor Skill | Trigger-description-driven Skill per enriched vendor | `decisions/0013` pt 1 | `skill.py::render_vendor_skill/write_vendor_skill` | Generated once a vendor is AI-enriched | Depends entirely on Feature 1/2/3 producing content — no independent evidence | Lead | Per-vendor `CLAUDE.md` (same content, different surface) | Low | ADAPTER | KEEP — content source is what's under evaluation (§5.1), not this renderer |
| 8 | Cursor `.mdc` export | Same content as per-vendor Skill, Cursor's own trigger model | `decisions/0013` pt 4 | `skill.py::render_cursor_mdc/write_cursor_mdc` | Generated alongside per-vendor Skill | No reference-project evidence either way (Ledgerkit/Technical Clipper evaluations are both Claude-Code-only so far) | Lead | Per-vendor Skill (same source content) | Low | ADAPTER | KEEP (small, already-paid-for, no signal to remove) |
| 9 | Root `CLAUDE.md` routing table | The literal file every session in the project auto-loads | Phase 4 | `index.py` | `init`/`sync`/bare `codecompass` | Real — this is CLAUDE.md's own generated table, visible at the top of this very file | Lead | Tool-level Skill (same vendor list, different surface) | Low | ADAPTER | KEEP |
| 10 | Per-vendor `CLAUDE.md` digest | Per-vendor grounding file | Phase 1 | `claude_md.py` | Read by `chat.py`, `index.py`, `staleness.py`, linked from Skills | Real, load-bearing — every other artifact points at it | Lead | None (single source of truth for per-vendor content) | Medium | CORE | KEEP |
| 11 | `/discovery` slash command | Guided, read-only exploration | Phase 17 | `commands.py` | Invoked by a human as `/discovery` | No direct evidence of invocation in either reference-project's evaluation logs (both evaluations used the CLI/graph directly, not `/discovery` itself) | Lead | Tool-level Skill (near-duplicate "how to explore" prose — §3) | Low-medium | ADAPTER | KEEP, see §3 for the duplication finding |
| 12 | `query` CLI subgroup | Programmatic, scriptable graph access | Phase 15+ | `cli.py::query_app` | Every evaluated reference-project task; `/discovery`'s own instructions point here | **The single most evidenced feature in the project** — every `context-evaluator`/`reference-project-tester` finding to date is a `query` interaction | Lead | n/a — this is the thing the others route to | Medium | CORE | KEEP |
| 13 | Ecosystem adapters (`adapters/`) | npm/Python/Cargo abstraction | `decisions/0002` | `adapters/{base,npm,python,cargo}.py` | `sync.py`, `discovery.py` | Real — every tracked vendor goes through this | Lead | None | Low (stable, unchanged in many phases) | CORE | KEEP |
| 14 | `discovery.py::rewrite_vendor_toml` | Wholesale `vendor.toml` rewrite | Only ever called by the now-retired `promote` command (`decisions/0018`, retired Phase 15/`decisions/0033`) | `discovery.py` lines 172–182 | **None** — grep confirms only its own definition + its own test reference it; no production call site anywhere in `cli.py` | None currently | Its own docstring already says "kept rather than deleted... a future command that needs to rewrite `vendor.toml` wholesale can reuse it" | Lead | n/a | Trivial (11 lines + 1 test) | REDUNDANT (dead code) | REMOVE — see §5.4 |
| 15 | Three planning queues (`context-gaps/`, `context-observations/`, `learnings/`) | Capture missing edges / edge-experience / process learnings, respectively | `decisions/0051` (gaps), Phase 52 (observations), original project convention (learnings) | Markdown-file inboxes + `check_user_docs.py` field checks + `knowledge-curator` triage | `knowledge-curator`, `reference-project-tester`, `context-evaluator` | Actively used and cross-referenced (`CG-002`/`L-016`/`L-019`/`OBS-001..006`) — each queue has already produced at least one real, traceable outcome | Lead + curator role | Conceptually adjacent (all three feed the same triage step) but each answers a genuinely different question (a request vs. an experience vs. a process lesson) | Low — process/doc only, no runtime code | CORE (process) | KEEP as three, see §3 |

## 3. Redundancy map

Three genuine overlaps found; no case of true duplicate *code*, only
duplicate *prose/content* or duplicate *purpose with different
mechanism*:

1. **Tool-level Skill vs. `/discovery` vs. `docs/cli-reference.md`** —
   all three independently enumerate the same `query` subcommand list
   and the same graph schema table names, hand-maintained in three
   places (`skill.py` lines 84–110, `commands.py` lines 66–85, and
   `docs/cli-reference.md`). Three phases already added a `query`
   subcommand (15, 21, 49-era) each requiring three edits kept in sync by
   convention, not by structure. This is a real, if low-severity,
   maintenance-burden finding — not a functional bug (all three are
   currently accurate).
2. **Direct-API relation enrichment vs. agent-driven relation
   enrichment** — same output table (`doc_relation_enrichment`), same
   validation path (`apply_results`), two producers distinguished only
   by the `model` column, by design (`decisions/0054`). This is the
   redundancy the prompt specifically asked to scrutinise — addressed in
   §5.1, not listed as a problem in itself (it was deliberately built as
   a second producer, not an accidental duplicate).
3. **`adapters/` (ecosystem) vs. the prompt's "adapter" (host-output)
   terminology** — a naming collision, not a functional overlap (see
   "Design decisions" above). No code changes; a doc clarification is
   enough.

No overlap found between the three planning queues (§2 row 15) beyond
sharing one triage owner — each has a distinct question it answers and
at least one real outcome attributable only to it.

## 4. Proposed target architecture

Not a `src/` restructuring (see "Design decisions"). The grouping below
is what `architecture/overview.md` gains a short new section stating
explicitly, using names already implicit in module docstrings today:

- **CORE** (host-agnostic, works identically whether Claude Code, a
  plain terminal, or some future agent runtime is driving it):
  `discovery.py`, `config.py`, `adapters/**`, `sync.py`, `symbols.py`,
  `filetree.py`, `deptree.py`, `usage.py`, `source_resolution.py`,
  `staleness.py`, `graph.py`, `claude_md.py` (the per-vendor digest is
  content, not a host-specific format), `query_app` (CLI subgroup),
  `enrich apply` (CLI subgroup — the trust-boundary check itself is
  host-agnostic even though today's only producer is a Claude Code
  agent).
- **AGENT** (reasoning that produces content CORE then persists through
  a CORE write-path): `enrichment.py`, `relation_enrichment.py` (the
  direct-API producers), `context-enrichment-agent.md` (the
  agent-driven producer) — three interchangeable *producers* for the
  same CORE-owned tables.
- **HOST-OUTPUT ADAPTERS** (format-specific renderers with no logic of
  their own beyond templating already-computed CORE/AGENT content):
  `skill.py` (Claude Skills + Cursor `.mdc`), `commands.py` (`/discovery`
  for Claude Code), `index.py` (root `CLAUDE.md` — a
  Claude-Code-and-friends convention, not universal).
- **SECONDARY / EVALUATION-PENDING**: `chat.py` — doesn't cleanly fit
  any of the above three tiers (it's a fourth, standalone consumption
  surface, not a producer and not a router); §5.2 covers whether it
  stays that way.

This grouping is documentation only this phase — see §7's implementation
sequence for the one-paragraph `architecture/overview.md` addition. It
gives a name to a distinction the codebase's own docstrings already
draw ("Batched, usage-driven AI enrichment" vs. "Templated (non-AI)
Skill..." are already two different registers in the source), rather
than inventing a new one.

## 5. Per-feature decisions

### 5.1 Direct-API enrichment (vendor/symbol AND relation) vs. agent-driven enrichment

**Candidates:** Features 1, 2, 3 (§2).

**Finding:** Phase 52 proved, live, that agent-driven enrichment can
fully replace the *relation*-level direct-API path with zero
`ANTHROPIC_API_KEY` dependency, at zero marginal implementation cost
beyond what already shipped. No equivalent agent-driven path exists yet
for *vendor/symbol*-level enrichment (Feature 1) — Phase 52's own
"Explicitly deferred" section named this "not needed to demonstrate the
lifecycle," not "impossible" or "not worth building."

Both direct-API modules remain the *only* path that has ever produced
real content in this project's own self-dogfooded `vendor/*/CLAUDE.md`
files (see the table at the top of this very `CLAUDE.md`: four vendors,
three enriched). Removing them outright would remove CodeCompass's only
currently-working way to enrich vendor/symbol content in an environment
that *does* have a configured API key (a real end-user's project, not
necessarily this dev environment) — the two producers serve different
environments, not different quality tiers.

**This is a genuine product-direction call, not a mechanical cleanup.**
Three real options exist, not one obvious answer:

- **(a) KEEP both direct-API modules unchanged**, treat agent-driven
  enrichment as strictly an availability fallback for the relation
  case only (today's status quo). Lowest risk, no change.
- **(b) GENERALISE agent-driven enrichment to also cover vendor/symbol
  enrichment** (a `context-enrichment-agent`-authored path into
  `enrichment.py`'s tables, mirroring `decisions/0054`'s pattern) so
  every enrichment surface has an API-key-free path, then re-evaluate
  whether the direct-API modules are still pulling their weight once
  both paths exist for everything.
- **(c) KEEP BUT NARROW**: leave both direct-API modules exactly as
  they are (real end-user value, real API-key environments), but stop
  citing "no `ANTHROPIC_API_KEY` available" as a reason to route around
  them in *this project's own* dogfooding — i.e., treat option (b) as
  unnecessary because the direct-API path was never actually broken,
  only unavailable in this one development environment, which agent-
  driven enrichment already and sufficiently covers for this project's
  own dogfood needs.

**Recommendation for the review gate:** (c) — do nothing to the two
direct-API modules; they have a real evidenced purpose (real end-user
projects with a configured key) that Phase 52's fixture demo doesn't
touch or threaten. Building (b) speculatively would be exactly the kind
of "design for hypothetical future requirements" this project's own
conventions warn against — there is no evidenced need for
vendor/symbol-level agent-driven enrichment yet, only the *shape* of a
precedent. Revisit only if a real need surfaces (an evaluation run in an
environment without `ANTHROPIC_API_KEY` that specifically needs
vendor/symbol content, not just relation content).

### 5.2 Chat REPL

**Candidate:** Feature 4.

`decisions/0034` already demoted chat from "the product" to "secondary,"
explicitly keeping it (not gating, not removing) after weighing exactly
this question once before, on the stated grounds that "it remains
genuinely useful for quick, digest-only Q&A in a plain terminal, and
removing working, tested code purely for a framing change is unwarranted
churn." Nothing has changed since that ADR that bears on its own
stated reasoning — no new evidence of harm, no maintenance burden spike
(132 lines, untouched in many phases), no conflicting feature has
appeared that chat now duplicates (`query vendor` answers a different
kind of question: structured facts, not conversational Q&A).

**Recommendation:** KEEP, unchanged. Re-litigating `decisions/0034`
without new evidence would violate the append-only ADR discipline in
spirit even if a new ADR is technically how it would be recorded — a new
decision should be driven by a new fact, and this phase's investigation
surfaced none. Noting explicitly for the review gate: if the user's
intent behind naming this in the prompt was "I suspect this is unused
and want it gone regardless of the prior ADR," that is a legitimate call
for the user to make directly — it is not something this plan
recommends unilaterally.

### 5.3 "Initial-chat" / project entry point / whole-project rollup

**Candidate:** Feature 5.

This does not exist as shippable code. It is the *never-built* Post-MVP
Phase 20/24 concept, explicitly deferred by `decisions/0048` and named
only in `chat.py`'s own docstring and one `planning/v1-redefinition/`
reference, both describing the same undelivered idea. There is nothing
to deprecate, narrow, merge, or remove.

**Recommendation:** No action beyond this finding itself. If Phase 24
(deferred, `decisions/0048`) is still a live future candidate, it stays
exactly where it already is in the roadmap's Post-MVP table — this
phase's job is rationalising what exists, not resolving a deferred
roadmap item's own fate.

### 5.4 Dead code: `discovery.py::rewrite_vendor_toml`

**Candidate:** Feature 14.

Confirmed via `grep -rln "rewrite_vendor_toml" src/ tests/`: exactly two
hits, its own definition (`discovery.py`) and its own dedicated test
(`tests/test_discovery.py`). No production call site — its only caller,
`promote`, was retired in Phase 15 (`decisions/0033`). Its own docstring
already flags this ("kept rather than deleted... a future command...
can reuse it") but no future command has needed it across 38 subsequent
phases.

**Recommendation:** REMOVE. This is the one item in this plan with an
unambiguous evidence bar met (zero callers, zero reference-project
signal, explicit dead-code docstring) and negligible risk (11 lines + 1
test, no schema/CLI/doc surface depends on it). Implementable directly
alongside this plan's own doc-only changes without a separate gate.

### 5.5 Skill / `/discovery` / `docs/cli-reference.md` command-list duplication

**Candidate:** §3 finding 1.

**Recommendation:** GENERALISE is tempting but oversized for the actual
problem — the prompt's own exclusions rule out new abstraction machinery,
and three hand-synced copies of a ~10-line command list, updated 3 times
in ~40 phases, is a real but small burden, not a correctness bug (none
of the three is currently wrong). DEFER: note the burden in
`architecture/overview.md`'s new §4-derived section (a one-line "these
three lists must be kept in sync by hand; there is no shared source"
caveat) rather than building a template-sharing mechanism now. Revisit
only if a future `query` subcommand addition is missed in one of the
three during a real phase (a recurrence, not a hypothetical).

### 5.6 `adapters/` naming collision

**Candidate:** §3 finding 3.

**Recommendation:** DEFER, doc-only. Add one sentence to
`architecture/overview.md`'s "Adapter interface" section distinguishing
"ecosystem adapter" (existing, `decisions/0002`) from "host-output
adapter" (this phase's new §4 vocabulary) so a future reader isn't
confused by the same word meaning two things. No rename — `adapters/`
is a stable, external-facing (tests import it) package name; renaming it
purely for vocabulary hygiene would be exactly the churn this project's
conventions warn against.

## 6. Compatibility implications

- **§5.4 (REMOVE `rewrite_vendor_toml`)**: no compatibility impact.
  Nothing outside its own test calls it; removing the test alongside it
  is a same-commit deletion, not a deprecation cycle.
- **§5.1, §5.2, §5.3, §5.5, §5.6**: no code change recommended this
  phase, so no compatibility surface changes. If the review gate instead
  selects option (b) from §5.1 (generalise agent-driven enrichment to
  vendor/symbol level), that would be net-additive (a new producer
  alongside the existing one, exactly `decisions/0054`'s own pattern) —
  zero breaking change to any existing caller, matching Phase 52's own
  precedent of a backward-compatible optional parameter.
- No CLI flag, config-schema, or generated-file-format change is
  proposed anywhere in this plan.

## 7. Implementation sequence

Only §5.4 and the doc-only items (§5.5, §5.6, plus §4's
`architecture/overview.md` addition) are pre-approved-shape work; the
rest waits on the review gate. If approved as recommended:

1. Delete `discovery.py::rewrite_vendor_toml` + its docstring reference
   in `render_vendor_block`'s neighbourhood + `tests/test_discovery.py`'s
   corresponding test(s). Confirm `ruff`/`pytest` clean.
2. Add `architecture/overview.md`'s new short section: the CORE / AGENT
   / HOST-OUTPUT ADAPTERS grouping from §4, the ecosystem-vs-host-output
   "adapter" disambiguation from §5.6, and the three-copies-hand-synced
   caveat from §5.5.
3. `docs-maintainer` reconciliation pass (confirms nothing else in
   `docs/`/`README.md`/`ai-docs/README.md` now conflicts with the new
   section; expected to find nothing, since no behavior changed).
4. `docs-reconstructor` per-phase drift audit.
5. Retro (this phase's own 9 retro questions, per the prompt).
6. `knowledge-curator` triage of anything this phase's own process
   surfaced (per the prompt's "Phase 53 should also serve as another
   real dogfooding exercise for the Phase 52 lifecycle" instruction —
   watch for a `context-gaps`/`context-observations` entry if a query
   made during this investigation itself surfaced friction, e.g. if
   `query relations` or `query skills` had been used to help build the
   feature inventory and something was found wanting).
7. `release-phase-auditor` pass.
8. `roadmap-context-curator` final reconciliation; commit; push per
   `CLAUDE.md` §6.

If the review gate instead selects (b) from §5.1, that becomes a
follow-on phase (54) with its own plan file, not folded into this one —
it is materially new code (an `EnrichmentCandidate`-shaped agent path
for `enrichment.py`), not a rationalisation of what exists.

## 8. Evaluation requirements

- §5.4's removal: `pytest`/`ruff`/`check_user_docs.py --strict` all
  clean, same bar as any other phase — no new evaluation instrument
  needed for dead-code removal.
- No reference-project re-evaluation is needed for this phase's approved
  scope (§7 items 1–2 touch no runtime behavior a `context-evaluator` or
  `reference-project-tester` run would observe).
- If a future phase pursues §5.1 option (b), that phase's own evaluation
  requirement is a live demonstration mirroring Phase 52's own two-cycle
  fixture pattern, adapted to vendor/symbol-level content — not
  prescribed further here since it isn't this phase's approved scope.

## 9. Acceptance criteria

Standard `CLAUDE.md` §5 Definition of Done, plus:

- The feature inventory (§2) and redundancy map (§3) are judged complete
  by the user at the review gate — i.e., the gate isn't just "approve
  §5's recommendations," it's also "confirm nothing you expected to see
  scrutinised is missing from §2."
- Every §5 recommendation is explicitly accepted, rejected, or deferred
  by the user before any code implementing it is written (this plan's
  own gate, restated).
- `rewrite_vendor_toml`'s removal (if approved) leaves `pytest`/`ruff`/
  `check_user_docs.py --strict` clean and produces no other diff.
- `architecture/overview.md`'s new section is judged accurate by
  `docs-maintainer`/`docs-reconstructor`, not just added.

---

## Review gate

This plan surfaces one small, unambiguous action (§5.4, dead-code
removal) and five genuine product-direction questions (§5.1's three
options, §5.2, §5.3, §5.5, §5.6) that this document deliberately does
not decide unilaterally. Per the prompt's own "Once the Phase 53 plan
has passed the normal review gate, implement the approved rationalisation
work," the next step is presenting §5's recommendations to the user for
an explicit accept/reject/defer decision on each, before any further
code is written.
