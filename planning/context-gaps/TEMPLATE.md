<!-- planning/context-gaps/TEMPLATE.md — copy into inbox.md, newest at top.
One relationship CodeCompass's context should hold but mechanical
detection does not / cannot produce. Governed by decisions/0051:
NEVER written to context-graph.db. -->

### CG-NNN — <one-line description of the missing relationship>

- **origin:** <phase / task that surfaced it; who observed it — lead or agent name>
- **date:** <YYYY-MM-DD>
- **codecompass_revision:** <short hash of CodeCompass at the time>
- **project:** <codecompass (own dev) | technical-clipper | ledgerkit> + <target commit if external>
- **the edge:** `A ↔ B` where A = <…>, B = <…>
- **edge kind:** <dependency↔dependency | dependency↔local-code | local-code↔local-code | doc↔code | behaviour↔test | other>
- **agent's reasoning:** <why the agent believes this relationship matters — what
  task it was doing, what it had to reconstruct by hand because the graph
  didn't connect these>
- **what the graph shows instead:** <the actual edges CodeCompass has between A
  and B today, or "none">
- **could mechanical detection ever catch this?**
  <yes-with-better-heuristics: name the heuristic (e.g. "same public-symbol
  name referenced across modules") | no-conceptual-only: it needs
  understanding, not pattern-matching | unsure>
- **smallest candidate that would fix it:** <conditional-generalisation.md §
  reference, or "new heuristic in <module>", or "unclear">
- **classification:** <detection-improvement (Stage C / GATE DB) | graph-capability (Stage E / GATE DD) | unsure>
- **status:** candidate
- **recurrence:** first occurrence
- **curation:** — <filled by knowledge-curator at triage. When the
  outcome is `discarded`, name the specific reason as one of the
  following controlled values (Phase 52), not just free prose — this is
  what lets GATE DB/DD later see the aggregate shape of "how often is
  this retrieval vs. detection vs. duplicate" across all discarded
  entries:
  `unsupported` (the claimed relationship doesn't actually hold once
  investigated) | `duplicate` (same underlying gap as another `CG-NNN`,
  merge instead) | `already_represented` (the graph already has this,
  the agent just didn't find it — a retrieval/discovery problem, not a
  detection gap) | `retrieval_issue` (the edge exists and is correct,
  but ranking/surfacing failed to show it) | `detector_gap` (a real,
  missing mechanical relationship — promotes to `promoted-to-roadmap`,
  Stage C / GATE DB, not `discarded`) | `graph_capability_gap` (needs a
  new edge/provenance kind entirely — promotes to `promoted-to-roadmap`,
  Stage E / GATE DD, not `discarded`). Only the first four values are
  ever paired with `status: discarded`; the last two are paired with
  `status: promoted-to-roadmap`.>
