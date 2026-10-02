# Phase 78 Stage 1 — treatment agent boundary-check result

```
Assigned directory: .../scratchpad/ledgerkit-treatment
Tool calls: 39 total (10 Read/Glob/Grep, 27 Bash, 1 Write/Edit)
Paths referenced outside the assigned directory:
  [Bash] /home/cormac/projects/codecompass/.venv/bin/python
```

The only out-of-scope reference is the explicitly-permitted `codecompass`
CLI executable invocation (the dispatch prompt told the agent to invoke
`/home/cormac/projects/codecompass/.venv/bin/python -m codecompass.cli`,
explicitly noting that executable is outside its read-scope but may be
invoked — confirmed no Read/Glob/Grep call ever targeted it or any
CodeCompass source/doc file). Zero references to the baseline clone, the
real Ledgerkit/CodeCompass repositories' own source, or
`planning/reference-projects/`.

**Verdict**: read-scope symmetry held for this arm.
