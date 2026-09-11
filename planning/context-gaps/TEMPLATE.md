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
- **curation:** — <filled by knowledge-curator at triage>
