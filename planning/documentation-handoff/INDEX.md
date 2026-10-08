# Handoff index and selection criteria

## Files in this handoff

- `README.md` — what/why/how, start here.
- `SOURCE-OF-TRUTH.md` — evidence hierarchy, conflict handling.
- `DOCUMENTATION-TARGET.md` — required output coverage/structure.
- `OPEN-QUESTIONS.md` — every currently-known open question/conflict
  across the selected knowledge slugs.
- `DISPOSITION-REPORT.md` — **orchestrator-facing only, not writer
  evidence** — records what happens to every pre-existing documentation
  file; included in this directory for the orchestrator's own later
  integration step, not because the writer needs it (it names old file
  paths, which carries no information the writer can act on from inside
  an isolated workspace with no access to those paths anyway).
- `knowledge/overview.md`, `invariants-and-constraints.md`,
  `interfaces-and-behaviours.md`, `tests-and-acceptance.md` — direct
  copies of the real, currently-rendered canonical projections for the
  selected slugs (see below), frozen at handoff-build time.
- `knowledge/workflows-and-state-transitions.md`,
  `edge-cases-and-compatibility.md` — curated syntheses (content-selected,
  not a render target), built by hand from the selected slugs' own
  canonical Claims.
- `knowledge/decisions-and-rationale.md` — a mechanically-generated
  title+status index over every ADR in `decisions/**` (the writer never
  sees the ADR corpus itself).
- `knowledge/source-and-evidence-map.md` — a mechanically-generated index
  from every Claim shown above to its own supporting Evidence's real
  `source_ref`/`doc_ref`/`test_ref`/`observations` trail.

## Handoff selection — which knowledge slugs, and why (plan §9.6, Amendment 6)

CodeCompass's own `planning/knowledge/` currently holds five slugs, all
five re-rendered and drift-checked for repository-wide consistency during
this preparation pass (`all_rendered_knowledge_slugs` in the manifest).
**Only four are selected into this handoff** (`handoff_selected_slugs`):

| Slug | Selected? | Reason |
|---|---|---|
| `codecompass-domain` | **Yes** | Project-wide domain knowledge — the clear, default case for a project-level redoc. |
| `first-party-source-symbols` | **Yes** | Describes a real, current CodeCompass capability (first-party source/symbol indexing) that a complete project redoc genuinely needs to explain. |
| `haskell-api-surface-extraction` | **Yes** | Describes a real, current CodeCompass capability (Haskell API surface extraction) for the same reason. |
| `doc-origin-pinned-reference` | **Yes** | Describes a real, current CodeCompass capability (doc-origin pinned-reference tracking) for the same reason. |
| `hledger-depth` | **No** | About a specific reference-project (Ledgerkit/hledger) engagement, not about CodeCompass's own implementation — exactly the case plan §9.6 names as *not* belonging in a project-level handoff by default, as distinct from a phase-scoped context packet, where it already correctly lives (`planning/knowledge/hledger-depth/context-packet.md`). |

This selection is the orchestrator's own judgment call, made and recorded
here — not an automatic "include everything that exists" default.
