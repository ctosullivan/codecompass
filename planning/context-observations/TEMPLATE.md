<!-- planning/context-observations/TEMPLATE.md — copy into inbox.md,
     newest at top. One record of real experience with an edge that
     already exists (or an honest "nothing existed" retrieval) —
     never a request for a missing edge (that's context-gaps/). -->

### OBS-NNN — <one-line: what was retrieved, was it used, outcome>

- **origin:** <phase/task — e.g. "Phase 46, Ledgerkit task 01">
- **date:** <YYYY-MM-DD>
- **codecompass_revision:** <short SHA>
- **project:** <codecompass (own dev) | ledgerkit | technical-clipper> (+
  target commit if external)
- **edge identity:** <the natural-key tuple this observation is about,
  in the same shape the relevant enrichment table already uses — e.g.
  `dev-docs/hledger-compatibility.md -- mentions_dependency --> (absent from graph)`
  or, once tracked, `... -- mentions_artifact -->
  .claude/skills/codecompass/SKILL.md`. If the observation is about the
  *absence* of an edge rather than one that exists, say so explicitly
  here — and consider whether it actually belongs in
  `planning/context-gaps/` instead (a request), not here.>
- **observation type:** <EDGE_USEFUL | EDGE_UNHELPFUL | EDGE_MISLEADING |
  EDGE_STALE | EDGE_REDUNDANT>
- **edge correctness:** <correct | incorrect | not-assessed> — was the
  mechanical claim itself true, independent of whether it helped.
- **task usefulness:** <useful | irrelevant-to-this-task | n/a> — did it
  help *this* task, independent of correctness. Never collapse this and
  "edge correctness" into one field.
- **default pathway:** <what a fresh agent without CodeCompass would
  have done to get the same information — concrete, not hand-waved>
- **advantage:** <LOW | MODERATE | HIGH> (`context-quality-evaluation.md`
  §5 definitions)
- **wrong or misleading?** <yes | no | partially> — expand if yes/partially
- **status:** <recorded | investigating | resolved>
- **investigation:** <filled only once status ≥ investigating — findings,
  evidence gathered, classification (unsupported / duplicate /
  already_represented / retrieval_issue / detector_gap /
  graph_capability_gap — same vocabulary `context-gaps/` uses, since an
  investigation of a bad edge and an investigation of a missing edge
  converge on the same outcomes)>
- **resolution:** <pointer to the CG-NNN / L-NNN / ADR / commit this fed,
  once one exists, or "no action — recorded as evidence">
