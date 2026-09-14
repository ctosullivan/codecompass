# Phase 52: Context edge lifecycle — observations queue + agent-driven enrichment

**Status:** done (2026-09-14). Delivered as scoped: the context-observations
lifecycle (migrated `context-use-log.md`, new `check_context_observation_fields`
check, `knowledge-curator` triage extended), `decisions/0054`'s agent-driven
enrichment (`apply_results`'s new `model` param, `codecompass enrich apply`,
the new `context-enrichment-agent`), and a real, live, two-cycle
demonstration against a local fixture (`tests/fixtures/ledgerkit_lifecycle_demo/`,
`DEMO.md`) — not the live Ledgerkit clone, per explicit user direction.
`pytest` 567 passed / 2 skipped, `ruff check .` clean, `check_user_docs.py
--strict` clean. `docs-reconstructor` drift audit
(`planning/retros/_drift-audit-phase-52.md`) → DRIFT, 2 non-blocking findings,
both fixed before commit. `release-phase-auditor`
(`planning/retros/_audit-phase-52.md`) → PASS WITH NON-BLOCKING OBSERVATIONS,
including independently live-reproducing the two-cycle demonstration itself;
the two actionable observations (a defensive `isinstance` check in `enrich
apply` + a `DEMO.md` wording fix) were addressed before closeout. Retro:
`planning/retros/phase-52-context-edge-lifecycle.md`. One real, honestly
disclosed complication during the live demo, root-caused and filed as
`L-019` (candidate). The Stage D-vs-Stage-F/G strategic decision (Phase 51's
retro) remains open and unaffected by this phase — this phase's scope came
from a direct user request, not from resuming that fork, and its fixture
demonstration deliberately did not touch the live Ledgerkit clone.

Implements `planning/context-edge-lifecycle-plan.md`'s N.1/N.2 scope,
plus two extensions the user requested during scoping on 2026-09-14:
(1) a new, narrow agent role performs enrichment when no
`ANTHROPIC_API_KEY` is available, instead of skipping the scenario
(`decisions/0054`); (2) the lifecycle is demonstrated against a **local
fixture** mimicking a real Ledgerkit roadmap feature, not the live
Ledgerkit clone, so nothing external is touched and the demo is
reproducible in CI/any environment.

Retargets Phase 52's roadmap slot (originally sketched as "Stage D —
deeper Ledgerkit dogfooding") to this scope, per the same
findings-drive-scope precedent Phase 49 already established against
Phase 48/49's original sketch mismatch.

## Depends on

- Phase 51 done (Stage C complete).
- `planning/context-edge-lifecycle-plan.md` (reviewed, this is its
  implementation).
- `decisions/0054` (Accepted, same day — the agent-driven-enrichment
  ADR this phase's scope required).

## Scope

**In scope:**

1. **Context-observations lifecycle** (plan §3.2/§6/§8, phase N.1/N.2):
   - `planning/context-observations/{README,TEMPLATE}.md`.
   - Migrate `context-use-log.md`'s existing entries into
     `planning/context-observations/inbox.md` as `OBS-NNN` records,
     content preserved verbatim, reshaped into the new fields. Leave a
     one-line pointer in the old file.
   - `context-gaps/TEMPLATE.md`: add the discard-reason controlled
     vocabulary (plan §3.3).
   - `scripts/check_user_docs.py`: new `check_context_observation_fields`
     (mirrors `check_learnings_candidate_fields`) + tests.
   - `.claude/agents/knowledge-curator.md`: extend to triage
     `context-observations/` (plan §5).
   - `.claude/agents/context-evaluator.md`,
     `.claude/agents/reference-project-tester.md`,
     `planning/agent-led-workflow.md` step 4: retarget the
     `context-use-log.md` pointer to `context-observations/`.

2. **Agent-driven enrichment** (`decisions/0054`):
   - `src/codecompass/relation_enrichment.py::apply_results` gains an
     optional `model: str = _MODEL` parameter (backward-compatible;
     `graph.record_relation_enrichment` already accepts an arbitrary
     `model` string, no `graph.py` change needed).
   - `src/codecompass/cli.py`: new `enrich` command group, one
     subcommand, `enrich apply`:
     - Args: a JSON file of agent-authored
       `{source_doc_path, target_vendor_name?, target_doc_path?,
       ai_summary, relation_label}` entries; `--agent <name>` (required).
     - For each entry, look it up against
       `relation_enrichment.select_candidates()`'s *current* output — if
       no matching candidate exists (the edge isn't real, or is already
       enriched and unchanged), reject that entry with a clear error.
       **This is the mechanism that enforces `decisions/0054` §4's hard
       boundary** — an agent cannot enrich a relationship that isn't
       already mechanically proven and pending enrichment; the CLI
       itself checks this, not agent good behaviour.
     - Validate `relation_label` via the existing
       `_normalize_relation_label`.
     - Build `RelationEnrichmentResult` from the matched candidate's own
       `content_hash` (never trust an agent-supplied hash) + the agent's
       `ai_summary`/`relation_label`.
     - Call `apply_results(conn, results, model=f"agent:{agent}")`.
     - Print a per-entry accepted/rejected summary.
   - New `.claude/agents/context-enrichment-agent.md` (`decisions/0054`
     §3): reads `select_candidates`'s pending list (via `query relations`
     on the source doc, or direct file inspection), writes a grounded
     `ai_summary` from the real excerpted text, calls `enrich apply`.
     Hard rules: only enriches edges `select_candidates` already lists
     as pending; never invents a relationship; no tool access to
     `context-graph.db` other than through `enrich apply`; no
     `src/codecompass/` writes.

3. **Local fixture + demonstration** (replaces a live Ledgerkit run,
   per explicit user direction):
   - `tests/fixtures/ledgerkit_lifecycle_demo/` — a minimal project
     mimicking Ledgerkit's own real, already-observed Stage A adoption
     of the CodeCompass Skill (confirmed real in the actual Ledgerkit
     clone: 8 `dev-docs/**/*.md` files mention "codecompass" by name,
     producing real `mentions_artifact` edges — Phases 45/46/49/51's own
     evidence). Contents: a `.claude/skills/codecompass/SKILL.md` (`name:
     codecompass` frontmatter, mirroring the real one) and two
     `dev-docs/*.md` files that mention "codecompass" in prose, mirroring
     the real Ledgerkit `dev-docs/retros/README.md`-style content.
   - **Cycle 1:** run `codecompass` (mechanical, `--budget 0`) against
     the fixture → confirm a real `doc_relations_edges` row exists
     (`query relations dev-docs/<file>.md` shows a `mentions_artifact`
     relation, not "not found," not enriched yet). Dispatch
     `context-enrichment-agent` against it → `enrich apply` writes a
     real `doc_relation_enrichment` row, `model = 'agent:
     context-enrichment-agent'` → confirm via `query relations` that the
     `ai_summary`/`relation_label` now appear. File one
     `context-observations/OBS-NNN` entry recording this as
     `EDGE_USEFUL` (the enrichment correctly explains a real relation).
   - **Cycle 2** (per the user's explicit "track over multiple cycles"
     instruction): add a third `dev-docs/*.md` file mentioning
     "codecompass," re-sync, re-run the enrichment agent against the new
     candidate only (confirm the *first* file's cached
     `doc_relation_enrichment` row is untouched — the content-hash cache
     still holds), file a second `OBS-NNN`. Confirm
     `context-observations/inbox.md` now has two entries, dated, IDed,
     distinguishable, and that neither `sync` run altered or duplicated
     the first cycle's audit records.

**Explicitly deferred / out of scope:**

- Vendor/symbol-level agent-driven enrichment (`enrichment.py`) —
  materially heavier (requires real cloned vendor source material,
  writes files to disk per `decisions/0038`'s own contrast) and not
  needed to demonstrate the lifecycle; `doc_relation_enrichment` alone
  fully exercises Scenario A. Revisit only if a real need appears.
- Touching the live Ledgerkit clone or repository in any way — per
  explicit user direction this phase uses a local fixture exclusively.
- The edge-request-lifecycle vocabulary sharpening (plan §3.3's
  `context-gaps/TEMPLATE.md` discard-reason enum) beyond adding the
  field guidance — no existing `CG-NNN` entry is retroactively edited.
- Any new CLI surface beyond `enrich apply` — no `context audit`/
  `context observations`/`context request` commands (plan §6.1's
  reasoning still holds for those; only the write-capability gap
  justified new surface).

## Design decisions

- **`enrich apply` enforces the trust boundary mechanically, not by
  agent instruction alone** — it only accepts entries matching a
  currently-pending `select_candidates()` row. An agent asked to enrich
  something that isn't a real, pending edge gets a hard CLI rejection,
  not a politely-declined request.
- **Reuse, don't fork, `apply_results`.** The only change to
  `relation_enrichment.py` is one optional parameter with a
  backward-compatible default — every existing call site, and every
  existing test, is unaffected.
- **The fixture mirrors real, already-observed Ledgerkit content**, not
  an invented scenario — the Skill-mention pattern is Ledgerkit's actual
  Stage A adoption of `adoption-blueprint.md`, independently confirmed
  real in Phases 45/46.
- **No ADR needed beyond `decisions/0054`** — the context-observations
  half of this phase is documentation/process, matching Phase 43c's own
  precedent for `context-use-log.md`'s original introduction.

## Files

- `planning/context-observations/{README,TEMPLATE}.md` — new
- `planning/context-observations/inbox.md` — new (migrated content)
- `planning/context-use-log.md` — pointer note added, not deleted
- `planning/context-gaps/TEMPLATE.md` — discard-vocabulary addition
- `scripts/check_user_docs.py` + `tests/test_check_user_docs.py` — new check
- `.claude/agents/knowledge-curator.md` — extended
- `.claude/agents/context-evaluator.md`,
  `.claude/agents/reference-project-tester.md` — pointer retargeted
- `.claude/agents/context-enrichment-agent.md` — new
- `planning/agent-led-workflow.md` step 4 — pointer retargeted
- `src/codecompass/relation_enrichment.py` — `apply_results` gains
  optional `model` param
- `src/codecompass/cli.py` — new `enrich apply` command
- `tests/test_relation_enrichment.py`, `tests/test_cli.py` — new tests
  for the `model` param and `enrich apply`
- `tests/fixtures/ledgerkit_lifecycle_demo/` — new fixture
- `docs/cli-reference.md` — `enrich apply` documented (`docs-maintainer`)
- `decisions/0054-agent-driven-enrichment-is-a-second-non-authoritative-producer.md` —
  already written (lead, same session)

## Verification

- `pytest` / `ruff check .` clean, including new tests for `enrich
  apply`'s acceptance/rejection paths (a real pending candidate accepted;
  a non-existent edge rejected; an already-enriched-and-unchanged edge
  rejected).
- `python scripts/check_user_docs.py --strict` clean.
- The two-cycle fixture demonstration actually runs (not just unit
  tests): real `codecompass sync`/`enrich apply`/`query relations`
  invocations against the fixture directory, output captured in the
  phase's own evidence (retro or a `tests/fixtures/ledgerkit_lifecycle_demo/DEMO.md`
  transcript).
- Confirm zero `context-graph.db` writes originate from anything under
  `planning/context-observations/**` or `planning/context-gaps/**` —
  the same sync-byte-identity-style check the original plan's §7 test
  plan specifies.

## Done when

Standard DoD + verification + the two-cycle local-fixture demonstration
completes with a real accumulated audit trail (two `OBS-NNN` entries,
two distinguishable enrichment events, one cache-hit correctly skipped)
+ `release-phase-auditor` PASS + learnings/context-gaps triaged.
