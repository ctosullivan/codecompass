# codecompass-template documentation disposition report

Built during Phase 81B preparation for `codecompass-template`'s own
lifecycle (plan §11), against that repository's real current state
(`bd2420d`, confirmed via `git log`/`git status` — clean working tree).
Classification per plan §9.5 (Amendment 5)'s structural-vs-narrative
split, not per-directory — `optional-intermediate-knowledge/**` and
`optional-clean-room-workflow/**` each mix both kinds.

| Path | Classification | Final action | Reason | Replacement |
|---|---|---|---|---|
| `README.md` | CURRENT NARRATIVE | Replace | Full redoc target | New `README.md` |
| `docs/architecture.md` | CURRENT NARRATIVE | Replace | Full redoc target | `docs/architecture.md` (writer's own finding) |
| `docs/worked-example.md` | CURRENT NARRATIVE | Replace | Full redoc target | `docs/worked-example.md` |
| `optional-intermediate-knowledge/README.md` | CURRENT NARRATIVE | Replace | Full redoc target, Amendment 1/5 — narrative prose, not structural, despite living beside structural content | Rewritten in place |
| `optional-intermediate-knowledge/worked-example.md` | CURRENT NARRATIVE | Replace | Same | Rewritten in place |
| `optional-clean-room-workflow/README.md` | CURRENT NARRATIVE | Replace | Same | Rewritten in place |
| `optional-clean-room-workflow/conceptual-documentation-guide.md` | CURRENT NARRATIVE | Replace | Same | Rewritten in place |
| `optional-clean-room-workflow/mechanical-isolation.md` | CURRENT NARRATIVE | Replace, likely updated with this phase's own real findings | Same, plus the backlog item's own "a short pointer... once a working approach exists" commitment — Phase 81B's own `unshare`/`pivot_root` mechanism is exactly such an approach, though the AI-writer credential blocker (§6.3) means it should be described honestly as a partial, not a full, resolution | Rewritten in place |
| `optional-clean-room-workflow/worked-example.md` | CURRENT NARRATIVE | Replace | Same | Rewritten in place |
| `optional-clean-room-workflow/{assertions,coding-context-selection,documentation-verification,implementation-comparison,legacy-reconciliation,propagation,snapshots}/TEMPLATE.md` (7 files) | STRUCTURAL | **No action — not narrative** | Blank, fillable skeletons (a real data shape a downstream adopter fills in), not explanatory prose | — |
| `decisions/TEMPLATE.md` | STRUCTURAL | **No action** | Same reasoning | — |
| `decisions/README.md` | GOVERNANCE-ADJACENT | **No action** | Explains the ADR *process* for downstream adopters, not product documentation about the template itself | — |
| `planning/CONTEXT.md`, `planning/ROADMAP.md`, `planning/context-gaps/README.md`, `planning/knowledge/README.md`, `planning/retros/TEMPLATE.md` | STRUCTURAL/GOVERNANCE SCAFFOLD | **No action** | Downstream-adopter scaffolding meant to be used as-is (mirroring CodeCompass's own planning conventions for a new adopter's own project), not narrative prose explaining the template | — |
| `vendor.toml`, `LICENSE`, `.gitignore` | STRUCTURAL | **No action** | Genuine configuration/package metadata | — |
| `CLAUDE.md` | OUT OF SCOPE | **No action** | Self-governing, not end-user/developer product documentation | — |

## Handoff selection note

`codecompass-template` has no `planning/knowledge/` of its own (plan
§9.5) — its own intermediary preparation is a direct synthesis from the
structural rows above only, independently grounded, never copied from
the narrative rows. Given Phase 81B's own authoritative writer run is
currently `BLOCKED` (`planning/phase-81b-mode-b-isolation-investigation.md`),
`codecompass-template`'s own clean-room branch was not built in this
implementation pass — the generic namespace/`pivot_root` isolation
mechanism this investigation already proved is repository-agnostic, and
building a second, mechanically-identical branch for this repository
would not change that verdict. This scope decision is recorded here
honestly rather than silently; building it remains a small, well-defined
follow-up once a real writer-run blocker (§6.3) is resolved.
