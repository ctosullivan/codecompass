# Packet sufficiency log — `doc-origin-pinned-reference`

Per `planning/phase-54c-evidence-knowledge-workflow.md` §6.1: every time
implementation needed something **not already in `context-packet.md`**
to make progress, logged here live, not reconstructed afterward.
Consulting a file/function the packet already *named* (its §7 pointer
list) is expected, normal use of the packet — not logged here. Only
genuinely missing information is.

## Gap 1 — `tests/test_graph.py` was never named as a test to update

**What was needed:** implementing `REQ-DOCORIGIN-001` (widen the
`_SCHEMA_VERSION` bump) broke 6 pre-existing tests in
`tests/test_graph.py` that hard-code the expected schema version string
(`assert schema_version == "6"`, in `test_init_schema_seeds_schema_version`,
`test_init_schema_is_idempotent`, and four `test_open_graph_migrates_pre_phase_*`
tests) — discovered only by running the *full* suite (`pytest -q`), not
from anything in the packet.

**Why the packet didn't have it:** §8 ("Existing tests") named only
`tests/test_spec_docs.py` and `tests/test_doc_mapping.py` — both real
and correctly scoped to `REQ-DOCORIGIN-002`/`-003` (the `scan_spec_docs`
detection logic), but `REQ-DOCORIGIN-001` (the schema/migration
requirement) has its **own** test file with its **own** hard-coded
expectations, and no record in the knowledge base ever inspected
`tests/test_graph.py` at all — the Context Researcher's own trace (§3 of
the design doc) covered every *code* consumer of `origin` exhaustively,
but not every *test* file asserting the schema version literal.

**Classification:** a one-off omission (the research traced code
consumers thoroughly but not this specific test file), not a structural
knowledge-base gap — the fix was mechanical once found (bump `"6"` to
`"7"` in 8 places, matching the exact precedent every prior
`_SCHEMA_VERSION` bump already required in this same file).

## Gap 2 — the Phase 17/21/27/32 "fresh-DB acceptance + migration test"
pair pattern was described narratively but not pointed at its own file

**What was needed:** `tests/test_graph.py` already has a repeating,
established test pattern for every prior enum widening — one
`test_doc_artifacts_accepts_<X>` test (fresh DB, new value inserts
without raising) plus one `test_open_graph_migrates_pre_phase_<N>_schema`
test (simulates an old on-disk schema, confirms migration + new value
acceptance). `REQ-DOCORIGIN-001`'s own example (§4 of the packet) is
close to this shape but doesn't reference the existing pattern by name,
so writing the two new mirroring tests required reading
`tests/test_graph.py` directly to find and copy the pattern, rather than
the packet pointing at it.

**Why the packet didn't have it:** §6 ("Relevant architecture") describes
the Phase 17/21/27 precedent narratively (drop-and-recreate, one generic
migration function) but doesn't name `tests/test_graph.py` as where that
precedent's own *test* pattern lives, separately from the *code*
pattern in `graph.py` the packet does name correctly.

**Classification:** related to Gap 1 (same missing file), but distinct
in kind — Gap 1 was "existing tests will break," this is "a new test
should follow an established pattern this file already has." Both point
to the same underlying, generalisable lesson: when a Requirement changes
a schema/migration mechanism specifically, the packet's "existing tests"
section should include the migration test file even if no Claim/Evidence
record happened to inspect it during research — worth naming for the
retro's own recommendation on packet-assembly guidance.

