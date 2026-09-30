# Docs-drift audit — Phase 79 (Clean-room conceptual understanding and documentation reconstruction)

Independent per-phase drift audit (`docs-reconstructor` MODE 1),
`planning/v1-redefinition/agent-led-development.md` §2.7, `CLAUDE.md` §5.

**Scope-correction note (kept here for the record):** the dispatch was
first given `b4641cc..HEAD` as the phase's diff range, but `b4641cc` is
itself a Phase 79 commit, not the commit before the phase started —
using that range silently excluded `scripts/check_knowledge_base.py`,
all six touched/added `.claude/agents/*.md` files, and part of the
`agent-led-development.md` edit. Re-run against the correct range,
`d241268..HEAD` (`d241268` = last Phase-78 commit, `ce7a69e^`), confirmed
via `git diff d241268..HEAD --stat` to be the full phase diff.

## Verdict: DRIFT — 4 findings, all non-blocking, all fixed

No `README.md`, `docs/` (outside `docs/domain/`), or `ai-docs/README.md`
user-facing statement was found false. All four findings were internal
governance-doc staleness (citation drift and catalogue-entry omissions),
not a misdescription of observable system behaviour for an external
reader.

### Finding 1 — stale line-citation in `docs/domain/concepts/claim.md`

`docs/domain/concepts/claim.md:123` cited
`scripts/check_knowledge_base.py:262-291` for
`check_supersedes_never_crosses_kind`. Phase 79 inserted ~140 lines of
new checker code ahead of that function (the enum/regex tables plus
`check_optional_enum_fields`/`check_list_fields_are_inline`), shifting
the real function to lines 419-447 (confirmed via
`grep -n "^def check_supersedes_never_crosses_kind"` → `419`, and reading
the function body through its closing `return findings` at line 447).

**Fixed**: citation updated to `scripts/check_knowledge_base.py:419-447`.

### Finding 2 — `agent-led-development.md` §2.4 (`docs-maintainer`) stale against its own agent file

Phase 79 added a whole new "Legacy reconciliation mode" section to
`.claude/agents/docs-maintainer.md` (five-way historical-claim
classification, a new write target
`planning/v1-docs-reconstruction/<topic-slug>/reconciliation.md`, a new
"fix it, don't just record" duty for a documentation-verification
finding). None of this appeared in §2.4's catalogue prose or the
write-boundary table's `docs-maintainer` row. Confirmed via
`git diff d241268..HEAD -- planning/v1-redefinition/agent-led-development.md`:
only §2.2/§2.11/§2.13/the new §2.14 were touched before this audit;
§2.4 was not.

**Fixed**: §2.4 gained a new bullet describing the legacy reconciliation
mode; the write-boundary table's `docs-maintainer` row gained the
`planning/v1-docs-reconstruction/**` write target.

### Finding 3 — `agent-led-development.md` §2.7 (`docs-reconstructor`) stale against its own agent file

`.claude/agents/docs-reconstructor.md`'s MODE 2 was rewritten this phase
to make a hardened, topic-scoped route (frozen snapshot +
implementation-reconstruction report as sole inputs, no legacy
narrative, self-selected architecture) "the default, not an opt-in"
whenever those two inputs exist for a topic. §2.7 still described MODE 2
as only "Blank-slate reconstruction (milestones only — Phase 64)."
Confirmed not touched in the same diff.

**Fixed**: §2.7 gained a new bullet describing the hardened,
topic-scoped route and when it applies.

### Finding 4 — `CONTRIBUTING.md`'s agent roster incomplete (pre-existing, made concretely worse this phase)

`CONTRIBUTING.md` (untouched by this phase's own diff — confirmed via
`git diff d241268..HEAD --stat -- CONTRIBUTING.md` returning nothing)
named only 7 specialist agents, omitting 6 real ones that already
existed pre-Phase-79 (`domain-skeptic`, `context-researcher`,
`documentation-agent`, `context-health-planner`,
`context-enrichment-agent`) plus this phase's own new
`implementation-reconstructor`. Pre-existing, but the new agent made the
omission concretely worse and it was in this audit's own scope
(agent-roster consistency), so flagged rather than deferred.

**Fixed**: roster line extended to name all 13 real agents.

## Confirmed clean (no drift)

- `architecture/overview.md`'s `core.Ecosystem` fix ("a 4-value enum
  (npm/python/cargo/haskell)") matches `src/codecompass/core.py:13-19`
  exactly.
- The new "Known fidelity limitations of `indexed_partial` and Python
  extraction" section in `architecture/context-graph-schema.md` checked
  line-by-line against `src/codecompass/source_symbols.py`: confirmed
  Python's top-level-only extraction (`ast.iter_child_nodes`, not a
  recursive walk) and the JS/TS `const`-as-literal-`kind` behaviour
  (direct keyword assignment, no right-hand-side inspection) both hold
  as described; the Rust/JS-TS line-scanners' lack of string-literal or
  plain-`/* */`-comment awareness structurally supports the claimed
  false-positive shapes (checked by code reading, not a live-executed
  repro against a crafted fixture in this specific audit pass — see
  scope note).
- `.claude/agents/implementation-reconstructor.md` matches
  `agent-led-development.md` §2.14 and its write-boundary-table row
  exactly.
- `.claude/agents/domain-skeptic.md`'s comparison mode and
  `.claude/agents/context-researcher.md`'s isolated mode match §2.13/
  §2.11 and their amended table rows.
- `ai-docs/README.md` mentions neither the specialist-agent roster, nor
  `check_knowledge_base.py`, nor the first-party-source/symbol
  subsystem — no contradiction possible.
- No `docs/`, `README.md`, or `ai-docs/README.md` sentence claims
  anything about `check_knowledge_base.py`'s own validation *scope* that
  the four new Phase 79 checker functions falsify.
- No domain-claim staleness candidates: no `docs/domain/**` concept
  page cites the first-party-source/symbol subsystem yet (nothing to go
  stale against); `docs/domain/concepts/ecosystem.md` already
  independently states the correct 4-value `core.Ecosystem` cardinality,
  unaffected by this phase; no domain-corpus citation of
  `architecture/overview.md` sits at or after the line range this phase
  edited.

## Scope note

Checked `scripts/check_knowledge_base.py`'s four new functions against
`docs/`, `README.md`, `ai-docs/README.md`, and every `docs/domain/**`
file that mentions it; checked both `architecture/` file diffs against
`src/codecompass/core.py` and `src/codecompass/source_symbols.py`;
checked all six touched/added `.claude/agents/*.md` files against
`agent-led-development.md`'s catalogue/write-boundary table and against
`ai-docs/README.md`/`CONTRIBUTING.md`. Did not re-verify the Rust
raw-string / JS-TS block-comment false-positive claims by executing the
extractors against a crafted fixture (structural code reading only — a
separate, independent completion audit pass later hand-traced the exact
Rust example and confirmed it). Did not audit the 76+ new
`planning/knowledge/first-party-source-symbols/**` files (not narrative
documentation, out of this role's scope). Did not audit
`CHANGELOG.md`/`planning/ROADMAP.md`/`planning/CONTEXT.md` content
accuracy (outside this role's `README.md`/`docs/`/`architecture/`/
`ai-docs/` remit — covered separately by the completion audit and the
terminal `roadmap-context-curator` reconciliation). Read-only
throughout; all four fixes above were applied by the lead after this
audit's own findings, not by this role.
