# Core concepts

**Provenance tier**: CLAIM-CITED. Every statement below is traced to a
specific Claim in CodeCompass's own approved domain-knowledge corpus,
snapshot `codecompass-overview@v1`. These are the project's own real,
already-vetted vocabulary — not re-derived from `src/` by this draft.
Citations use the form `codecompass-overview@v1#CL-XXX-NNN`.

This file is split into two halves on purpose. The first half is the
**product vocabulary** — the concepts a user, contributor, maintainer,
or agent actually runs into when using or extending CodeCompass. The
second half is CodeCompass's own **internal development-process
vocabulary** (Evidence/Claim/Observation/Decision/Requirement) — the
scheme CodeCompass's own project team uses to record *how it knows what
it knows about itself*. A reader only needs the second half if they are
working on CodeCompass's own knowledge base (as this draft's inputs
were); it is not part of the product CodeCompass ships to its users.

## Product vocabulary

### Ecosystem, vendor, adapter

These are three distinct, related concepts, not synonyms
(`codecompass-overview@v1#CL-ADPT-005`):

- **Ecosystem** — a fixed, closed 4-member category: `npm`, `python`,
  `cargo`, `haskell`. It is not something a project configures per
  instance; it classifies *how* a dependency is packaged.
- **Vendor** — one tracked third-party dependency: a
  `VendorConfig(name, ecosystem)` entry, belonging to exactly one
  Ecosystem (e.g. a vendor named `hledger-lib` under the `haskell`
  ecosystem). Many vendors can share one Ecosystem.
- **Adapter** — the concrete class implementing ecosystem-specific logic
  for one Ecosystem value, constructed fresh per `(VendorConfig,
  project_root)` via a closed dispatch table (`get_adapter`) — never
  chosen by naming convention, plugin discovery, or a config string
  (`codecompass-overview@v1#CL-ADPT-001`). Many vendors sharing an
  Ecosystem share one adapter *class* but each still gets its own
  adapter *instance*, scoped to that vendor's own config and
  `project_root`. Edge case worth knowing: "one vendor, one adapter
  instance" is not a structural filesystem guarantee — a single
  `project_root` can host multiple vendors' worth of source (a
  monorepo checkout), and narrowing that down to the one subdirectory
  for a given vendor is the adapter instance's own responsibility
  (`codecompass-overview@v1#CL-ADPT-005`).

Two adapter *implementation strategies* coexist by deliberate design,
not as one superseding the other: an in-process strategy (an importable
Python class inside CodeCompass itself, shelling out to native ecosystem
tooling — the default, lower-overhead strategy) and an external-process
strategy (a thin in-process dispatcher delegating real ecosystem-specific
logic to an independent OS process speaking a small JSON-Lines protocol,
intended for ecosystems whose implementation cannot or should not live
in-process) (`codecompass-overview@v1#CL-ADPT-002`). Only the in-process
strategy's one concrete example (`PythonAdapter`) is independently
confirmed in this draft's evidence base; see `08-limitations-and-provenance.md`.

A caution on nearby vocabulary: **"connector" is not a real CodeCompass
concept** — it names nothing in this project's source, docs, or
decisions; if encountered, the nearest real concept is "adapter"
(`codecompass-overview@v1#CL-ADPT-004`). **"Capability" and "feature" are
not interchangeable**: "capability" is the external adapter protocol's
own closed, four-value term (`dependencies`, `symbols`, `observations`,
`diagnostics`) gating what an external adapter may legitimately report;
"feature" is ordinary, unscoped English used throughout project prose
with no enumeration or schema attached
(`codecompass-overview@v1#CL-ADPT-006`). And **"adapter" itself is a
known fuzzy boundary**: this project's own architecture material uses
the bare word for two different things — the real `EcosystemAdapter`
class family, and an informal "host-output adapter" label for
modules that render output (not independently covered by this draft;
see the out-of-scope list) with no shared base class at all
(`codecompass-overview@v1#CL-ADPT-007`). When this draft says "adapter"
unqualified, it means `EcosystemAdapter`.

### context-graph.db and "context"

"Context" has no single canonical meaning in this project — it names at
least five genuinely distinct, related-but-not-interchangeable things
(`codecompass-overview@v1#CL-CTXT-001`):

1. **`context-graph.db`** — the deterministic SQLite persistence layer
   of vendors, symbols, and edges. This is the one sense with a direct,
   confirmed-live implementation counterpart; see
   `04-architecture-persistence.md`.
2. **"The context CodeCompass supplies to an agent"**, generally — an
   informal umbrella covering digests, graph query output, generated
   Skills, `/discovery`, and chat answers together, not one artifact.
3. A **"context packet"** — a narrowly-scoped, human-reviewed planning
   artifact (see "Digest vs. context packet" below); this sense belongs
   to CodeCompass's own development process, not to the product's
   runtime behavior.
4. Three distinct **assessment instruments** (not independently covered
   by this draft) for judging how well sense (2) is working.
5. **"Context" as plain English** inside unrelated internal names (e.g.
   a role named `roadmap-context-curator`), meaning planning-doc state,
   not runtime context at all.

When this draft says "the graph" or "context-graph.db," it always means
sense (1).

### Digest vs. context packet

A **digest** (`VendorDigest`) is a per-vendor aggregate combining
deterministic, always-free output (file tree, dependency tree, API
surface) with a read-only lookup of that vendor's existing AI enrichment,
rendered unconditionally on *every* whole-project sync, for *every*
tracked vendor, under `vendor/<name>/`
(`codecompass-overview@v1#CL-CTXT-005`). A **context packet** is a
mechanically and purposively different thing: a curated Markdown artifact
produced *once* per feature, only after that feature's own design
document reaches an approved status, gated on human/lead review, living
under CodeCompass's own planning tree rather than `vendor/`
(`codecompass-overview@v1#CL-CTXT-002`). No context packet is ever
produced automatically the way a digest is, and no digest is ever gated
on human approval the way a context packet is. The word "digest" is also
used informally in three overlapping (not conflicting) ways in project
prose: the `VendorDigest` object itself, the full per-vendor file set
collectively, and specifically a vendor's own `CLAUDE.md` text — worth
knowing when reading other CodeCompass material, even though it does not
change the technical definition above (`codecompass-overview@v1#CL-CTXT-005`).

### Relationship / edge

"Relationship" and "edge" are used precisely for one thing: a real, typed
row in one of **six edge tables** in `context-graph.db` —
`uses_edges`, `documents_edges`, `skill_mentions_edges`,
`routes_via_edges`, `depends_on_edges`, `doc_relations_edges` — each
deterministically detected and rebuilt on every whole-project sync
(`codecompass-overview@v1#CL-CTXT-003`). This precise sense deliberately
excludes two neighboring things: an agent-suggested relationship that
has not been mechanically proven (never written into `context-graph.db`
at all), and an AI-authored commentary about an already-real edge
(enrichment data, not itself an edge, and carrying no foreign key back to
the thing it comments on) (`codecompass-overview@v1#CL-CTXT-003`).

A closely related but structurally separate pair of tables —
`git_worktrees` and `git_submodules` — satisfies the *same* wipe/
reinsert-every-sync lifecycle as the six edge tables above, but is not
counted among them: every one of the six edge tables has at least one
endpoint among the four content entities a vendor/doc/symbol query
traverses (vendors, symbols, source files, doc artifacts), while the
git-topology tables connect only to a self-contained `git_repositories`
entity that no content table ever references
(`codecompass-overview@v1#CL-CTXT-006`). This is a real, previously
implicit architectural line, not an arbitrary omission — see
`04-architecture-persistence.md` for the concrete schema.

### Reference

"Reference" is used in at least three genuinely distinct senses, never
unified in one place before this phase
(`codecompass-overview@v1#CL-CTXT-004`):

- (a) a `doc_artifacts.origin = 'pinned_reference'` row — a graph-level
  provenance value classifying externally-sourced, revision-pinned
  material materialized into the project tree (confirmed at the schema
  level; see `04-architecture-persistence.md`);
- (b) a **reference project** — a whole external codebase used as ground
  truth for evaluating CodeCompass's own output quality (a process
  concept, not covered further by this draft);
- (c) a **citation/pointer field** on an internal knowledge record or
  concept page, resolving to a real file:line location — the same
  citation discipline this draft itself follows; see
  `08-limitations-and-provenance.md`.

## CodeCompass's own development-process vocabulary

This vocabulary describes how CodeCompass's project team records and
vets claims about CodeCompass itself (including the very documents this
draft is built from). It is internal process, not product behavior — a
user of CodeCompass the tool never encounters it.

- **Evidence** (`EV-<feature>-NNN`) — a strictly neutral package of one
  or more Observations, or a direct source/doc/test citation, describing
  what was found. It never itself asserts support or contradiction of
  anything; that relationship is recorded only by whichever Claim later
  cites it (`codecompass-overview@v1#CL-EVID-001`).
- **Observation** (`OBS-<feature>-NNN`) — a single, dated, reproducible
  act of looking (running a command, reading a specific file, fetching a
  specific URL). Never itself a claim about behavior; its own status is
  always "recorded," never promoted or contradicted directly
  (`codecompass-overview@v1#CL-EVID-002`).
- **Derivation** (`DE-<feature>-NNN`) — records the reasoning *process*
  behind a Claim: what was traced, in what order, including mistakes
  made and how they were caught. A narrative field, not a formal proof
  (`codecompass-overview@v1#CL-EVID-004`).
- **Claim** (`CL-<feature>-NNN`) — an agent's interpretation built from
  one or more Evidence records; the only place a support/contradict
  relationship is recorded, with a closed status enum (`proposed`,
  `supported`, `contradicted`, `superseded`, `verified`) and no numeric
  confidence score (`codecompass-overview@v1#CL-EVID-012`). Every Claim
  cited in this document, and the snapshot this draft was built from, is
  an instance of this record kind.
- **Decision** (`DEC-<feature>-NNN`) — the one record kind only a human
  or project owner authors or explicitly ratifies; records *chosen*
  target-project behavior, never a revision of observed upstream
  behavior (`codecompass-overview@v1#CL-EVID-005`).
- **Requirement** (`REQ-<feature>-NNN`) — an implementation-facing,
  testable statement citing the Decision that authorizes it, with a
  Given/When/Then example and a closed status enum
  (`codecompass-overview@v1#CL-EVID-006`).
- **"Invariant"** is *not* one of the above record kinds and has no
  dedicated schema; it is used informally for at least three different
  artifacts with different promotion mechanisms, not interchangeably
  (`codecompass-overview@v1#CL-EVID-007`).
- **"Provenance"** is never a record kind of its own; it is a
  cross-cutting property realized with a structurally different concrete
  shape in each of at least three mechanisms in this project (the
  Evidence/Claim record fields; a single `model` column on the graph's
  enrichment tables; narrative fields on process-observation entries)
  (`codecompass-overview@v1#CL-EVID-013`).

**A naming collision worth knowing about**: these file-based
Evidence/Claim/Observation/Decision records describe CodeCompass's own
development process. A separate, *not-yet-built, not-funded* candidate
design has sketched graph-level (`context-graph.db`) entity kinds using
the *same* names to represent provenance about *other projects'*
dependencies. These are genuinely different concepts sharing four words,
and the collision is real, evidenced, and deliberately left open rather
than resolved by this draft
(`codecompass-overview@v1#CL-EVID-011`, `codecompass-overview@v1#CL-EVID-012`).
One narrow, independently corroborated fact: as of this evidence base,
no graph-level "claim," "evidence," or "observation" entity kind
currently exists in `context-graph.db`'s real schema (see
`04-architecture-persistence.md` for the exhaustive confirmed table
list) — the candidate design remains exactly that, a candidate.

There are, in fact, at least **five** distinct "something was
noticed/recorded" mechanisms in this project at different trust levels
(Observation records; a planning-only gap-tracking mechanism;
a planning-only experience-logging mechanism; a process-lesson queue;
and AI-authored graph enrichment, the only one of the five that writes
inside `context-graph.db` itself) — none interchangeable with, or a
special case of, another (`codecompass-overview@v1#CL-EVID-010`). The
details of the planning-only mechanisms are process documentation outside
this draft's product-facing scope; the one mechanism with a direct
product counterpart (AI-authored graph enrichment: `vendor_enrichment`,
`symbol_enrichment`, `doc_relation_enrichment`) is covered in
`04-architecture-persistence.md`.
