# Phase 80 Part 4 — coding-context packet evaluation

Independent `context-evaluator` assessment of
`_part4-coding-context-packet.md` (the task: add
`codecompass query source-stats`), against `src/codecompass/cli.py`,
`graph.py`, and `tests/test_cli.py` directly. Kept as a result SEPARATE
from documentation accuracy (see `_part4-reader-qa-verification.md`),
per the governing instruction.

**Verdict: FAIL. Advantage rating: LOW.**

## What was accurate

The packet's schema claim is correct — `graph.py` (`source_files.symbol_index_status
TEXT CHECK (... IN ('indexed','indexed_partial','unsupported','parse_error','unreadable'))`),
nullable.

## What was materially wrong (the FAIL trigger)

The packet asserted its own named precedents — `query topology`, `query
source`, `query source-symbol` — "use the graph's own open-or-note
pattern" (`_open_graph_or_note`/`_graph_session`), and handed the
implementer a code skeleton built on `_graph_session`. **This is false.**
All three actually use a distinct helper, `_open_graph_if_exists`
(`cli.py:895-912`), whose own docstring states it is "deliberately not a
change to the shared `_open_graph_or_note`/`_graph_session` helpers,"
plus an additional gate on `graph.get_meta(conn, "source_index_version")
is None` with command-specific "not yet indexed" rendering. Following
the packet's skeleton verbatim would wire the new command to the wrong
helper and silently drop the `source_index_version` gate every sibling
`source_files`-reading command enforces.

Also wrong: the packet cited `query topology`'s boolean tri-state
rendering as the precedent for "never collapse NULL," but the actually
on-point precedent — never mentioned in the packet — is
`_render_symbol_index_status` (`cli.py:1051-1067`), which already
renders this exact column's `NULL` as `"unknown"`. The packet instead
invented a new label, `"not_yet_indexed"`, inconsistent with established
vocabulary for this very field.

Test-coverage gap mirrors the pattern gap: `test_cli.py` has a standard
scenario for every `source_files`-reading command — db exists but
`source_index_version` was never written — which the packet's three
listed test cases omitted entirely.

## Root cause

Traced directly: the error originates in the Stage 2 model-blind
reconstruction report's own §2 CLI-surface summary, which overgeneralized
"every `query`/`enrich` subcommand that needs the graph uses a
consistent open-or-note pattern (`_open_graph_or_note`/`_graph_session`)"
— collapsing two related-but-distinct helpers into one, because the
reconstruction could only read `cli.py`, never execute it (see that
report's own §0). This inaccuracy propagated into the Stage 4 fresh
draft (`02-cli-reference.md`, `06-extension-points.md`,
`07-agent-orientation.md`) and survived Stage 3's comparison (out of
scope — the frozen snapshot's own Claims are conceptual/meta-level, not
CLI-helper-naming-level, so Stage 3 had no basis to catch it) and Stage
5's reconciliation (also out of scope — the real existing docs never
state this implementation-detail-level claim either way, so there was
nothing for reconciliation to conflict-check it against). **It only
surfaced via this packet's own downstream use and independent
evaluation** — exactly why the coding-context-packet check is kept
separate from, and not substitutable for, the documentation-accuracy
checks. All four affected Stage 2/4 files corrected in place with dated
notices (originals preserved, not rewritten).

## Context-advantage reasoning

A developer simply told "add `query source-stats`, go read the code and
follow the sibling `query source`/`source-symbol` commands" would have
discovered `_open_graph_if_exists`, the `source_index_version` gate, and
the `"unknown"` label themselves by reading the actual sibling
functions — and would not have been anchored on the packet's incorrect
framing. The packet's one accurate contribution (schema) is a one-line
grep away. The packet would have misled an implementing agent on the
graph-open helper/pattern, the missing `source_index_version` gate, and
the `NULL`-label terminology, all stated with unqualified confidence.
