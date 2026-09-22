---
status: APPROVED (2026-09-23, actual user/domain owner, subject to corrections applied same day)
---

# Context

## Definition

"Context" is not one artifact in this project — it is an umbrella word
used for at least five genuinely distinct, related-but-not-interchangeable
things. This page names each sense explicitly rather than picking one and
calling it canonical, because no single canonical definition currently
exists in the repository (`CL-CTXT-001`).

1. **`context-graph.db`** — the deterministic SQLite persistence layer of
   vendors, symbols, usage, docs, and their edges
   (`src/codecompass/graph.py`). See [`relationship-edge.md`](relationship-edge.md).
2. **"The context CodeCompass supplies to an agent"** (informal umbrella)
   — everything a consuming agent might actually read: per-vendor
   digests, graph query output, generated Skills/`.mdc` rules, the
   `/discovery` slash command, `codecompass chat` answers. This sense has
   no single artifact backing it — it names a *category* of things, not a
   file or table.
3. **A "context packet"** (`context-packet.md`) — Phase 54c's own
   specific, curated, feature-scoped Implement-stage artifact. See
   [`context-packet.md`](context-packet.md). This is the *narrowest* and
   most precisely-defined of the five senses, and the one most likely to
   be confused with sense 2 or with a digest precisely because it is also
   "a bundle of context for an agent."
4. **Assessment/logging instruments over sense 2**: `planning/context-health.md`
   (forward-looking, whole-graph readiness, owned by `context-health-planner`),
   `planning/context-use-log.md` (superseded by `planning/context-observations/`
   — a high-volume log of whether a real retrieval beat the default
   pathway), and `context-quality-evaluation.md` (`context-evaluator`'s
   per-task, retrospective "did this help" judgment against a target
   repository). None of these three is sense 2 itself — each *evaluates
   or logs the use of* context CodeCompass already produced
   (`EV-CTXT-005`).
5. **"Context" as a plain-English word inside an unrelated agent name** —
   `roadmap-context-curator` uses "context" to mean planning-doc state
   (what's done, what's next), not runtime context at all.

The project's own closest-to-canonical top-level statement — ai-docs/
README.md's "produces per-vendor digests plus a SQLite context graph" —
already treats "context graph" (sense 1) and "digest" as two separate,
coordinate nouns rather than collapsing everything into one "context"
concept (`EV-CTXT-006`). That is consistent with, not contradicted by,
the five-way split above.

## What this is NOT

- **Not one file, one table, or one artifact.** There is no single thing
  in this repository you can point to and say "that is the context."
- **Sense 1 (`context-graph.db`) is not sense 3 (a context packet).** The
  graph is mechanically rebuilt, project-wide, on every sync. A context
  packet is curated once, per feature, gated on human/lead review of an
  `APPROVED` `design.md`. A context packet may *cite* graph query output
  read-only, but is never generated from or synchronized with the graph
  automatically.
- **Sense 2 (the informal "what an agent gets") is not the same as a
  digest.** A digest is one specific, per-vendor, deterministic-plus-
  enrichment rendering (see [`digest.md`](digest.md)); sense 2 also
  includes the graph, Skills, chat, and packets — a digest is one
  *instance* of sense 2, not a synonym for it.
- **Sense 4's three instruments are not interchangeable with each
  other.** `context-health.md` is forward-looking and whole-graph;
  `context-use-log.md`/`context-observations/` is a high-volume per-
  retrieval log; `context-quality-evaluation.md` is a deep, per-task,
  reference-project-grounded report. Conflating any two loses real
  information about what each is actually for.

## Invariants

- `context-graph.db` (sense 1) is never written to by an agent's
  subjective interpretation — only by deterministic detection
  (`rebuild_deterministic`) or the two/three narrowly-scoped enrichment
  writers (`decisions/0051`, `decisions/0054`). This holds regardless of
  which of the other four senses of "context" a given piece of work is
  talking about.
- A context packet (sense 3) is never itself a source of new "context
  graph" fact — it is a downstream, curated projection of already-
  `APPROVED` knowledge-base records, never the reverse.
- The assessment instruments (sense 4) never produce sense-1 or sense-3
  artifacts as a side effect — `context-health-planner` and
  `context-evaluator` are both read-only with respect to
  `context-graph.db` and never write a context packet.

## Example

`ai-docs/README.md`'s own opening line: "produces per-vendor digests plus
a SQLite context graph of vendors, symbols, usage, and how a project's
own docs relate to them" — one sentence, two coordinate nouns, neither
one called simply "context" as if the other didn't exist (`OBS-CTXT-008`).

## Counterexample / fuzzy boundary

**Genuinely fuzzy**: sense 2 (the informal umbrella, "the context
CodeCompass supplies to an agent") has no hard boundary — is a Skill
generated from the graph "context" in the same sense as the graph
itself, or is it a *consumer* of context? Is a `codecompass chat` answer
itself "context," or is it an *answer produced from* context (sense
2 applied to sense-1 data)? This project's own documentation does not
draw this line consistently, and this phase's own research did not find
evidence that it needs to be drawn precisely for any current mechanism
to work correctly — it is a real looseness, not (yet) a real defect. This
is left as an open observation, not resolved further here
(`docs/domain/open-questions.md`).

## Relationships

- **Subsumes**: nothing cleanly — this is the fuzziest, least well-
  bounded concept in this cluster precisely because it is an umbrella
  term, not a single mechanism.
- **Is distinct from**: [`context-packet.md`](context-packet.md) (one
  specific curated artifact), [`digest.md`](digest.md) (one specific
  per-vendor rendering), [`relationship-edge.md`](relationship-edge.md)
  (the graph's own mechanical rows).
- **Is evaluated/logged by**: `context-health.md`, `context-use-log.md`/
  `context-observations/`, `context-quality-evaluation.md` — each a
  distinct instrument over sense 2, none of them sense 2 itself.

## References

- `CL-CTXT-001` / `DE-CTXT-001` — `planning/knowledge/codecompass-domain/`
- `EV-CTXT-001`, `EV-CTXT-003`, `EV-CTXT-004`, `EV-CTXT-005`,
  `EV-CTXT-006` — `planning/knowledge/codecompass-domain/`
- `ai-docs/README.md:1-40`
- `.claude/agents/context-health-planner.md:1-40`
- `planning/context-health.md:1-30`
- `planning/context-use-log.md:1-30`
- `planning/v1-redefinition/context-quality-evaluation.md:1-60`
- `src/codecompass/graph.py:50-360`
