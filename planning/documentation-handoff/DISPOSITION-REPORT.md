# CodeCompass documentation disposition report

Built during Phase 81B preparation, at `documented_revision` `46601a1`
(`feat(phase-81b): knowledge-layer preparation...`), before any clean-room branch is
frozen, per `planning/phase-81b-clean-room-redocumentation.md` §8.3.
Every pre-existing human-facing narrative documentation file in this
repository is listed here with its classification and planned final
action. **This report records a plan, not yet an executed state** — the
"final action" column names what will happen at integration (§16), after
a verified Mode B writer run actually produces replacement documentation;
nothing listed here has been deleted or archived yet. This file is
re-checked against the real tree at integration time to confirm every
row's planned action genuinely happened (§8.3, §18 item 10).

Classification legend (plan §7.1):

- **CURRENT NARRATIVE** — current-truth prose describing the project as
  it exists now; superseded by this phase's own fresh reconstruction.
- **HISTORICAL/GOVERNANCE** — decision history or process record;
  preserved unconditionally, never in scope for this phase's own
  disposition (plan §7.4).
- **OUT OF SCOPE** — self-governing project-operation file, not
  user/developer-facing documentation, untouched by Phase 81B entirely.

| Path | Classification | Final action | Reason | Replacement | Archive location | Refs to update |
|---|---|---|---|---|---|---|
| `README.md` | CURRENT NARRATIVE | Replace | Full redoc target | New `README.md` | — | All internal links into `docs/**` |
| `docs/quickstart.md` | CURRENT NARRATIVE | Replace, likely renamed | Full redoc target | `docs/getting-started.md` (plan §12.1) | — | `README.md`, `ai-docs/README.md` |
| `docs/cli-reference.md` | CURRENT NARRATIVE | Replace, likely renamed | Full redoc target | `docs/reference/cli.md` | — | `README.md`, `ai-docs/*`, `CONTRIBUTING.md` |
| `docs/config-schema.md` | CURRENT NARRATIVE | Replace, likely renamed | Full redoc target | `docs/reference/configuration.md` | — | `README.md`, `docs/quickstart.md`'s replacement |
| `docs/codecompass-knowledge-workflow.md` | CURRENT NARRATIVE | Replace, likely relocated | Full redoc target | `docs/workflows/knowledge-workflow.md` (writer's own evidence-based placement) | — | `README.md`'s grounded region (see note below), `CONTRIBUTING.md` |
| `docs/external-adapters.md` | CURRENT NARRATIVE | Replace, likely relocated | Full redoc target | `docs/reference/protocols.md` or `docs/architecture/components.md` (writer's own finding) | — | `docs/developer/*`, `architecture/adapter-interface.md`'s replacement |
| `docs/developer/writing-an-adapter.md` | CURRENT NARRATIVE | Replace, likely relocated | Full redoc target | `docs/development/writing-an-adapter.md` or folded into `contributing.md` | — | `CONTRIBUTING.md`, `docs/external-adapters.md`'s replacement |
| `docs/developer/haskell-adapter-submodules.md` | CURRENT NARRATIVE | Replace, likely relocated | Full redoc target | `docs/development/` (writer's own finding) | — | `docs/developer/writing-an-adapter.md`'s replacement |
| `docs/protocol-adapter/wire-protocol.md` | CURRENT NARRATIVE | Replace, likely relocated | Full redoc target | `docs/reference/protocols.md` | — | `docs/protocol-adapter/integrating-a-new-external-adapter.md`'s replacement |
| `docs/protocol-adapter/integrating-a-new-external-adapter.md` | CURRENT NARRATIVE | Replace, likely relocated | Full redoc target | `docs/reference/protocols.md` or `docs/development/` | — | `docs/external-adapters.md`'s replacement |
| `docs/domain/README.md` | CURRENT NARRATIVE (Amendment 2/7 — no standing exemption) | Replace | Semantic content re-grounded via knowledge pipeline (§9.1) into the handoff before any writer sees it; original is narrative prose like any other | `docs/concepts/` index (writer's own finding) | — | Every `docs/domain/*` cross-reference |
| `docs/domain/concepts/*.md` (18 files) | CURRENT NARRATIVE (Amendment 2/7) | Replace | Same as above — reconstructed from validated knowledge, not copied | `docs/concepts/*.md` (writer's own finding) | — | `docs/domain/glossary.md`, `docs/domain/quick-reference.md`, `docs/domain/references.md` |
| `docs/domain/glossary.md`, `quick-reference.md`, `examples.md`, `invariants.md`, `open-questions.md`, `references.md` | CURRENT NARRATIVE (Amendment 2/7) | Replace | Same as above | Folded into the writer's own `docs/concepts/` structure or a dedicated glossary page | — | Internal `docs/domain/` cross-links |
| `architecture/overview.md` | CURRENT NARRATIVE | Replace | Full redoc target | `architecture/overview.md` (writer's own content, same path plausible) | — | `README.md`, every other `architecture/*` file |
| `architecture/core-data-model.md` | CURRENT NARRATIVE | Replace | Full redoc target | `docs/architecture/data-and-control-flow.md` or similar | — | `architecture/overview.md`'s replacement |
| `architecture/adapter-interface.md` | CURRENT NARRATIVE | Replace | Full redoc target | `docs/architecture/components.md` | — | `docs/external-adapters.md`'s replacement |
| `architecture/context-graph-schema.md` | CURRENT NARRATIVE | Replace | Full redoc target | `docs/architecture/data-and-control-flow.md` or a dedicated schema page | — | `architecture/overview.md`'s replacement |
| `architecture/sync-and-enrichment-pipeline.md` | CURRENT NARRATIVE | Replace | Full redoc target | `docs/architecture/data-and-control-flow.md` or `docs/workflows/` | — | `architecture/overview.md`'s replacement |
| `architecture/module-map.md` | CURRENT NARRATIVE | Replace | Full redoc target | `docs/architecture/components.md` | — | `architecture/overview.md`'s replacement |
| `architecture/historical-notes.md` | CURRENT NARRATIVE, named edge case | **Incorporate-then-delete, OR archive** (Amendment 4 — "leave untouched" removed as an option; the choice between these two is made with real evidence once the writer's own output exists, not pre-decided here) | Amendment 4 | Fresh architecture narrative (if incorporated) | `docs/archive/historical-notes.md` (if archived instead) | `architecture/overview.md`'s replacement either way |
| `ai-docs/README.md` | CURRENT NARRATIVE | Replace | Full redoc target | `ai-docs/README.md` (same path plausible — agent-orientation pointer stays useful) | — | `CLAUDE.md`'s own routing (verify after replacement, do not edit `CLAUDE.md` itself) |
| `ai-docs/CLAUDE.md` | CURRENT NARRATIVE | Replace | Full redoc target | `ai-docs/CLAUDE.md` (same path plausible) | — | — |
| `CONTRIBUTING.md` | CURRENT NARRATIVE | Replace, stays at repo root (GitHub discovery convention) | Full redoc target | New `CONTRIBUTING.md` | — | `README.md`, `docs/developer/*` replacements |
| `decisions/**` | HISTORICAL/GOVERNANCE | **No action** | Append-only governance record, out of scope (plan §7.4) | — | — | — |
| `planning/retros/**`, `planning/ROADMAP.md`, `planning/CONTEXT.md`, `planning/learnings/**` | HISTORICAL/GOVERNANCE | **No action** | Project history/provenance, out of scope (plan §7.4) | — | — | — |
| `CLAUDE.md` (root) | OUT OF SCOPE | **No action** | Self-governing project-operation file, not end-user/developer product documentation — governs how sessions work on this repository, not what the repository does | — | — | — |

## Notes

- **`docs/codecompass-knowledge-workflow.md`'s replacement must account
  for `README.md`'s own real `codecompass-grounded-by` region** (citing
  `CL-KNOW-001`, migrated to `region:intermediate-knowledge-layer` in
  Phase 81's own third corrective pass). The fresh writer does not see
  this marker (it is inside the excluded `README.md`), so the
  orchestrator must re-apply an equivalent grounding marker to whatever
  region of the *new* README covers this same material, once the new
  README exists — otherwise Phase 81's own knowledge-layer grounding
  mechanism silently loses its one real production anchor. This is a
  required integration-step action item (§16), not optional cleanup.
- Every "likely relocated" replacement path above is the writer's own
  expected, evidence-based finding, not a structure this phase forces
  (plan §12.1) — the table names a plausible destination so a reviewer
  can sanity-check the writer's actual output against *something*, not a
  binding requirement.
- `docs/domain/**`'s own disposition is the direct, explicit application
  of Amendments 2 and 7: successful rendering of its *meaning* into the
  knowledge-preparation stage (§9.1) does not exempt the *files themselves*
  from the same reconstruct/delete/archive decision every other narrative
  document receives.
