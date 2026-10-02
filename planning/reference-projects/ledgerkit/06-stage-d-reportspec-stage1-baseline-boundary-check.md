# Phase 78 Stage 1 — baseline agent boundary-check result

```
Assigned directory: .../scratchpad/ledgerkit-baseline
Tool calls: 29 total (13 Read/Glob/Grep, 14 Bash, 1 Write/Edit)
Paths referenced outside the assigned directory:
  [Bash] /home/cormac/projects/codecompass/.venv/bin/python
```

The only out-of-scope reference is the explicitly-permitted pytest
executable invocation (the dispatch prompt told the agent it may invoke
this binary to run Ledgerkit's own test suite, just not read its own
source — confirmed no Read/Glob/Grep call ever targeted it). Zero
references to the other arm's clone, the real Ledgerkit/CodeCompass
repositories, or `planning/reference-projects/`.

**Verdict**: read-scope symmetry held for this arm.
