# 0049. Agent-led development model — lead session + small specialist roster

## Status

Accepted (Phase 39 records it; the roster itself is built in Phase 40).
Full design: `planning/v1-redefinition/agent-led-development.md`.

## Context

`decisions/0048` redefines CodeCompass v1 as a product-validation
milestone. Its first prerequisite (Stage A) is that CodeCompass becomes
its own first agent-led development project: the tool is positioned as
"the context layer for AI development agents" but is not itself developed
that way, has no independent evaluation of the context it produces, and
has no systematic capture of what agents learn while building or testing
it.

The project already has relevant precedent:
`planning/v0.2-implementation-execution-plan.md` records a subagent
incident (a research subagent deleted files despite explicit read-only
instructions, root-caused to unrestricted Bash access) and established a
standing rule: "verify independently, every time, not just when something
feels off." The agent-led model generalises that rule into a small set of
roles with real permission boundaries.

## Decision

Adopt the model in `planning/v1-redefinition/agent-led-development.md`:

**A lead Claude Code session acts as project lead** — understands the
requested phase, coordinates and integrates implementation, delegates
bounded work, resolves conflicts between agent outputs, ensures the
`CLAUDE.md` process is followed, and owns the commit and all `src/`
changes (directly or via an ad-hoc implementer subagent).

**CodeCompass never spawns or orchestrates agents.** Claude Code (or
equivalent tooling) is the orchestration layer — a hard boundary.

**A capped specialist roster** (`.claude/agents/`), each with
model/tools/isolation frontmatter and the write boundaries in the design
doc's §3 table:

| Agent | Purpose | Independent? |
|---|---|---|
| `context-evaluator` | rate the context CodeCompass supplied (accuracy / relevance / completeness / freshness / grounding / noise / trustworthiness; PASS / PASS WITH GAPS / FAIL + LOW/MODERATE/HIGH advantage) by inspecting the target repo **directly** | yes |
| `reference-project-tester` | exercise CodeCompass against real projects; file friction findings; never silently repair CodeCompass to make its own eval pass | partial |
| `docs-maintainer` | reconcile current-truth docs against verified implementation; rewrite weak prose; remove obsolete statements rather than appending caveats | no |
| `roadmap-context-curator` | reconcile `ROADMAP.md` / `CONTEXT.md` / `CHANGELOG.md` / `planning/**` from project evidence; never mark a phase done because code was written | no |
| `knowledge-curator` | own the project-learning lifecycle (`planning/learnings/`); promote / retain / merge / discard candidate learnings into the artifact that owns each | no |
| `docs-reconstructor` | at milestones only: blank-slate documentation reconstruction as a shadow proposal | yes |
| `release-phase-auditor` | read-only Definition-of-Done audit; `PASS` / `PASS WITH NON-BLOCKING OBSERVATIONS` / `FAIL` (a `FAIL` blocks completion); never repairs what it audits | yes |

**Fixed points:**

- Specialist agents operationalise the *existing* governance mechanisms
  (`CLAUDE.md`, `ROADMAP.md`, `CONTEXT.md`, ADRs, `architecture/`, tests,
  `CHANGELOG.md`, §5's DoD, §0's protected-file rule). No agent maintains
  a private parallel system.
- Evaluation and audit agents inspect their target directly, never via
  CodeCompass, and never repair what they are judging.
- **No agent writes `CLAUDE.md`, `decisions/*`, or `src/`** — the lead
  owns those; ADRs go through `CLAUDE.md` §2's process; `CLAUDE.md`
  changes go through §0.
- **An agent observation is not authoritative because an agent recorded
  it.** It enters the learning lifecycle
  (`planning/v1-redefinition/learning-lifecycle.md`) as a candidate; only
  curation plus evidence promotes it into a test, ADR, doc, roadmap row,
  rule, or skill. Agent persistent memory is a per-agent working aid,
  never a source of truth.
- The roster is **start-here, prune-at-GATE-DA**: Phase 43 dogfoods the
  full loop on one real change and its retro amends or removes roles that
  didn't earn their keep.

**Definition-of-Done integration** (proposed `CLAUDE.md` §5 amendment,
gate G4, landed in Phase 40–42): every phase additionally requires that
candidate learnings are triaged by `knowledge-curator` and that an
independent `release-phase-auditor` pass (or an explicit lead
confirmation for a trivial phase) verifies the existing six conditions
rather than trusting the implementing agent's report; reference-project
phases additionally require a linked `context-evaluator` report.

## Alternatives considered

- **Keep ad-hoc subagent delegation** (the current
  `v0.2-implementation-execution-plan.md` pattern) with no standing
  roles. Rejected: it provides no independence guarantee, no continuous
  doc/roadmap maintenance, and no systematic learning capture — all of
  which every later stage of `decisions/0048` depends on.
- **A larger roster mirroring every software-development activity**
  (dedicated security / performance / test-writing / implementer
  agents). Rejected: those are activities within a phase, not
  separations of context, responsibility, or authority; a bigger roster
  is a complexity and coordination cost (risk R9 in the planning
  package). Use `/security-review`, `/code-review` etc. as skills
  instead.
- **CodeCompass orchestrates its own specialist agents.** Rejected — a
  hard non-goal; CodeCompass discovers, selects, connects, grounds,
  retrieves, and explains technical context, and nothing else.

## Consequences

- Phase 40 creates `.claude/agents/*.md` and `planning/agent-led-workflow.md`
  (the 12-step fresh-session procedure).
- `CLAUDE.md` gains a new §8 (agent-led model) and an amended §5 (DoD) —
  both `CLAUDE.md` §0-gated, presented as an exact diff for approval
  before being written (gate G4).
- `CONTRIBUTING.md` mirrors whatever `CLAUDE.md` subset is approved, in
  the same commit (the `decisions/0022`/`0030` precedent).
- `knowledge-curator` owns `planning/learnings/`; a follow-up ADR
  (`0050`) records the learning-lifecycle rules if Phase 41 surfaces a
  non-obvious tradeoff.
- GATE DA (Phase 43) may amend this roster; such an amendment is a
  planning-doc + `.claude/agents/` change, not a new ADR unless it
  reverses a fixed point above.
- **Roster extended in Phase 43c** (2026-09-11): an 8th agent,
  `context-health-planner` (forward-looking "is the graph adequate for
  the upcoming roadmap" assessment; writes `planning/context-health.md`
  only). GATE DA kept the roster at 7 with no pruning; this addition does
  not reverse a fixed point above (it uses CodeCompass read-only, writes
  one planning file, files `context-gaps/` rather than editing the
  graph), so it is a planning-doc + `.claude/agents/` change per the line
  above. The non-obvious tradeoff it comes packaged with — agent-suggested
  context is captured, never graphed — is its own ADR, `decisions/0051`.
