# Docs-drift audit — Phase 53 (legacy feature rationalisation)

**Scope:** the phase's implementation diff (dead-code removal +
`architecture/overview.md` additions), checked against current-truth
docs (`README.md`, `docs/`, `architecture/`, `ai-docs/`). Independent
re-derivation from source, not from `docs-maintainer`'s summary of what
it changed. Run by `docs-reconstructor`; this file backfills the report
artifact after the fact — the audit itself was dispatched and completed
before `release-phase-auditor`'s pass, per the standard per-phase gate,
but its report wasn't saved to `planning/retros/` at the time. Caught as
a process gap (missing evidence-trail artifact, not a substantive
finding) in `release-phase-auditor`'s first-round audit; see
`planning/retros/_audit-phase-53.md` for that audit's own full,
multi-round report.

**Verdict: NO DRIFT.**

## What was checked

1. **`discovery.py::rewrite_vendor_toml` removal**: `git diff` confirmed
   only the function + its docstring were deleted from
   `src/codecompass/discovery.py`, and only its corresponding test
   (`test_rewrite_vendor_toml_overwrites_with_fresh_configs`) plus its
   import were deleted from `tests/test_discovery.py`. No other code
   referenced it (`append_vendor_toml`/`write_vendor_toml` untouched).
   `grep -rn "rewrite_vendor_toml"` across the whole repo: zero hits in
   `README.md`, `docs/`, `architecture/`, `ai-docs/` — it was never
   documented as a user-facing feature, so nothing needed updating.
2. **`architecture/overview.md`'s two additions** (the `## Adapter
   interface` disambiguation sentence; the new `## Module tiers: CORE,
   AGENT, HOST-OUTPUT ADAPTERS` section) — spot-checked every module-to-
   tier claim against the real code:
   - `discovery.py`, `config.py`, `sync.py`, `symbols.py`, `filetree.py`,
     `deptree.py`, `usage.py`, `source_resolution.py`, `staleness.py`,
     `graph.py`, `claude_md.py` — host-agnostic, no Claude-Code-specific
     dependency; CORE classification holds.
   - `enrichment.py`, `relation_enrichment.py` (direct-API producers) and
     the `context-enrichment-agent` role (`decisions/0054`, confirmed
     `Accepted` and matching) — AGENT classification holds; `enrich
     apply` (`cli.py:1104`) confirmed genuinely host-agnostic (plain JSON
     file, graph-state trust boundary).
   - `skill.py`, `commands.py`, `index.py` — each renders a Claude-Code/
     Cursor-specific artifact format from already-computed content;
     HOST-OUTPUT ADAPTER classification holds.
   - `chat.py` — its own docstring already calls it "a secondary,
     digest-only tool," matching the new "SECONDARY" bullet and the
     pre-existing `## Chat REPL` section's `decisions/0034` citation
     further down the same file. Reinforces existing text, no
     contradiction.
   - `adapters/base.py` — confirmed as the ecosystem-adapter ABC
     (`EcosystemAdapter`, `decisions/0002`), correctly distinguished from
     "host-output adapters" by the new disambiguation sentence.
3. **"Three hand-synced copies" claim** — verified true by direct
   comparison: `skill.py::render_tool_skill`, `commands.py::render_
   discovery_command`, and `docs/cli-reference.md` each independently
   enumerate the identical 5-subcommand `query` list
   (`vendors`/`vendor`/`symbol`/`skills`/`relations`) with matching
   flags. No shared template — the caveat is accurate.
4. **Reverse check** (existing doc broken by the new additions): grepped
   `README.md`, `ai-docs/README.md`, `docs/*.md` for "adapter" and
   "chat" — every existing "adapter" usage refers consistently to the
   ecosystem-adapter sense (`decisions/0008`, `config-schema.md`,
   `cli-reference.md`); none would be confused by the new disambiguation.
   `ai-docs/README.md` has zero hits for "core/tier/adapter/host-output"
   — nothing there to contradict.
5. **Deterministic check**: `python scripts/check_user_docs.py --strict`
   → `check_user_docs: no findings` (internal links, `codecompass`
   example commands, and ADR cross-references all clean, including the
   new `../docs/cli-reference.md` link and the `decisions/0054`/
   `decisions/0002` references added).

## Out-of-scope item noted, not attributed to this phase

`architecture/overview.md` lines 10-44 (the "As of Phase 19..." snapshot
paragraph) lists CLI commands as `query (vendors/vendor/symbol/skills)`
— missing `relations` and `enrich`, which post-date Phase 19. This
predates Phase 53 and this phase's diff didn't touch it; flagged as a
pre-existing staleness item (candidate for the Phase 61 reconciliation),
not a Phase-53-caused finding.

## Scope note

Checked: `src/codecompass/discovery.py`, `tests/test_discovery.py`,
`architecture/overview.md`'s diff in full, `src/codecompass/
{enrichment,relation_enrichment,skill,commands,index,chat,cli}.py`,
`src/codecompass/adapters/base.py`, `docs/cli-reference.md`,
`README.md`, `ai-docs/README.md`, `decisions/0054-*`,
`.claude/agents/context-enrichment-agent.md`. Not independently
re-verified: `planning/` files (planning-only, not current-truth docs
under this audit's charter) and the Phase 61 architecture-split
candidate list itself (unrelated to this phase's diff).
