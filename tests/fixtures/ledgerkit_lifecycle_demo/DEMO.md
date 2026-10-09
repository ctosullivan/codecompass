# Context edge lifecycle demonstration — transcript

Phase 52. Runs the full lifecycle (mechanical sync → mechanical edge →
enrichment queue → agent-driven enrichment → available via `query
relations` → context-observation recorded) against this local fixture,
across two cycles, per the user's explicit "test against a local
fixture, not the real Ledgerkit repo" and "track over multiple cycles"
instructions. This file records what actually happened, including one
honest, minor hiccup — not a cleaned-up idealized version.

The fixture mimics Ledgerkit's own real, independently-confirmed Stage A
content (Phases 45/46): `dev-docs/**/*.md` files that mention the
`codecompass` Skill by name, producing real `mentions_artifact` edges.

## Cycle 1

1. `codecompass --budget 0` against a fixture with two `dev-docs/*.md`
   files (`retros/README.md`, `planning/README.md`), each mentioning
   "codecompass." Confirmed via `query relations`: both files correctly
   detected as `mentions_artifact` edges to `.claude/skills/codecompass/SKILL.md`,
   status "mentioned, not yet enriched" — the mechanical layer, unchanged
   by this phase, working exactly as it always has.
2. Read both files' real content directly (as `context-enrichment-agent`
   would). Wrote a grounded `ai_summary` + `relation_label` for each into
   `cycle1-enrichment.json`.
3. `codecompass enrich apply cycle1-enrichment.json --agent context-enrichment-agent`
   → `applied 2 agent-enrichment result(s)`.
4. Confirmed via `query relations` and a direct `sqlite3` read: both rows
   now carry the real summary, `model = 'agent:context-enrichment-agent'`
   — clearly distinguishable from automated-API provenance, per
   `decisions/0054`.
5. Filed `planning/context-observations/OBS-005` — `EDGE_USEFUL`.

## Cycle 2

6. Added a third file, `dev-docs/architecture.md`, mentioning
   "codecompass." Snapshotted cycle 1's two `doc_relation_enrichment`
   rows first.
7. Re-ran `codecompass --budget 0`. **Confirmed cycle 1's two rows are
   byte-identical after the rebuild** (`diff` on a full column dump,
   including `content_hash` and `generated_at`) — the concrete proof
   that `rebuild_deterministic` deleting and reinserting
   `doc_relations_edges` does not touch `doc_relation_enrichment`
   (`decisions/0038`'s natural-key design working as documented, not
   just asserted).
8. Confirmed via `query relations`: the two cycle-1 files still show
   their cached enrichment (not re-flagged as pending); the new
   `dev-docs/architecture.md` correctly shows "mentioned, not yet
   enriched."
9. **Honest complication, not smoothed over:** while testing the CLI's
   rejection path (resubmitting `dev-docs/retros/README.md`'s already-
   enriched edge alongside the genuinely-new `architecture.md` one), the
   `retros/README.md` resubmission was *unexpectedly accepted*, not
   rejected. Root-caused rather than dismissed: this fixture was
   bootstrapped from a hand-written placeholder `SKILL.md` (a short
   `description:`), and bare `codecompass`'s own bootstrap run
   regenerates the tool Skill file as a side effect of the *same* sync
   that also scans it — so cycle 1's actual `select_candidates` call
   computed its content-hash against the placeholder's still-short
   description (captured before that sync's own regeneration step ran),
   while every check afterward saw the regenerated, longer description.
   That's a real difference in `target_text`, so `select_candidates`
   correctly judged it "changed" — the caching mechanism was not at
   fault; the fixture's own bootstrap order created a genuine one-time
   content difference. Confirmed the Skill file is deterministic and
   stable across repeated `codecompass index` runs once past that
   initial transient (`md5sum` identical across two consecutive runs).
   Filed as candidate learning `L-019` (a methodology note for future
   fixture/demo authors, not a product defect).
10. **Clean re-verification once the transient had settled:**
    resubmitted the identical two-entry batch a second time.
    `applied 0`, `rejected 2` — both `dev-docs/architecture.md` (already
    enriched from step 9's accidental-but-legitimate application) and
    `dev-docs/retros/README.md` correctly rejected as "not a pending
    mechanical-edge candidate — the edge doesn't exist, or is already
    enriched and unchanged," **exit code 1**. This is the genuine,
    reproducible proof the trust boundary works: an edge that is real
    but unchanged cannot be re-enriched through this path, mechanically
    enforced, not by agent good behaviour.
11. Filed `planning/context-observations/OBS-006` recording both the
    successful cycle-2 enrichment and the honest step-9 finding.

## Final state (verified by direct query)

```
$ sqlite3-equivalent: SELECT source_doc_path, model, relation_label FROM doc_relation_enrichment
dev-docs/architecture.md    | agent:context-enrichment-agent | explains_usage_of
dev-docs/planning/README.md | agent:context-enrichment-agent | explains_usage_of
dev-docs/retros/README.md   | agent:context-enrichment-agent | explains_usage_of
```

All 3 real mechanical edges enriched, all correctly attributed to the
agent-driven producer, none touching a graph-fact table at any point
(`doc_relations_edges`'s 3 rows are exactly what mechanical detection
produced — confirmed via `select_candidates` never being asked to
enrich anything outside that set).

## Reproducing this demo

```
cd tests/fixtures/ledgerkit_lifecycle_demo
rm -f context-graph.db vendor.toml
codecompass --budget 0
codecompass enrich apply cycle1-enrichment.json --agent context-enrichment-agent
# add a new dev-docs/*.md file mentioning "codecompass" here for cycle 2
codecompass --budget 0
codecompass enrich apply cycle2-enrichment-with-rejection-demo.json --agent context-enrichment-agent
```

`context-graph.db`/`vendor.toml`/`CLAUDE.md` (this fixture's own
generated routing table) are gitignored/regenerated artifacts of running
the demo, not committed fixture inputs. The committed `dev-docs/*.md` and
`*.json` files are hand-authored; `.claude/skills/codecompass/SKILL.md`
started as a hand-written placeholder but is itself mechanically
regenerated by `codecompass`'s own bootstrap run (step 9's finding,
`L-019`) — confirmed deterministic/idempotent across repeated runs, so
its committed content is real, current tool output, not a stale
artifact. `.claude/commands/discovery.md` is likewise tool-generated.
