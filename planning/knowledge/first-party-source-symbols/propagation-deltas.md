# Propagation demonstration (Phase 79 §10.4)

Disposable fixture, built under the session scratchpad (never inside
either repository's tracked tree), deleted after this report was
written. No synthetic change, contradiction, or `CONTROLLED TEST` record
was ever left in real canonical `planning/knowledge/first-party-source-symbols/`,
real snapshots, or real published documentation.

## Fixture contents

- `source/source_symbols.py` — a real copy of
  `src/codecompass/source_symbols.py`.
- `knowledge/OBS-FIX-001.yaml`, `EV-FIX-001.yaml` — an Observation and an
  Evidence record whose `source_ref` cites the fixture's own copy of the
  source file above.
- `knowledge/CL-FIX-001.yaml`, `CL-FIX-002.yaml`, `CL-FIX-003.yaml` — three
  Claims: `CL-FIX-001` is directly supported by `EV-FIX-001`;
  `CL-FIX-001.depends_on = [CL-FIX-002]` and
  `CL-FIX-002.depends_on = [CL-FIX-001]` form a genuine two-node cycle,
  constructed deliberately for this fixture; `CL-FIX-003.depends_on =
  [CL-FIX-001]` is a real transitive dependent reaching into the cycle
  from outside it. Each Claim has its own Derivation
  (`DE-FIX-001/002/003.yaml`).
- `snapshots/snapshot-v1.toml` — a frozen snapshot citing `CL-FIX-001`.
- `context-packets/context-packet.md` and `docs/domain-page.md` — both
  cite the snapshot (`fix-propagation-demo@v1`).

## Change made

`source/source_symbols.py`'s own module docstring, in the fixture's own
copy only — never the real file — to exercise source-to-evidence
discovery (§10.1) rather than editing an assertion directly.

## Propagation trace (real output, `propagation_traversal.py`)

1. **Source → Evidence** (grep `source_ref` for the changed path):
   found `EV-FIX-001` (cites `source/source_symbols.py:1-20`).
2. **Evidence → Claim** (grep `supporting_evidence`): found `CL-FIX-001`.
3. **Transitive dependents, cycle-safe** (visited-set walk from the seed
   claim): visit order `CL-FIX-001 → CL-FIX-003 → CL-FIX-002`.
   `CL-FIX-002 → CL-FIX-001` was attempted next and skipped — `CL-FIX-001`
   was already in the visited set, so the walk terminated cleanly rather
   than looping. All 3 claims visited exactly once.
4. **Snapshot-level citation**: `snapshots/snapshot-v1.toml` flagged —
   its own `[assertions."CL-FIX-001"]` table cites an assertion now in
   the affected set.
5. **Both derived-output kinds**: both `context-packets/context-packet.md`
   and `docs/domain-page.md` re-flagged `needs reassessment` — both cite
   `fix-propagation-demo@v1`, the same snapshot flagged in step 4, from
   the same underlying source change.

## Cycle handling

Confirmed: the `CL-FIX-001 ↔ CL-FIX-002` cycle was walked exactly once
each. The visited-set check fired exactly once (`CL-FIX-002 → CL-FIX-001`,
already visited), which is what makes termination provable here rather
than merely assumed — without it, this traversal would loop indefinitely
between `CL-FIX-001` and `CL-FIX-002`.

## Fixture deleted

Confirmed — the entire `phase79-propagation-fixture/` directory (built
under the session scratchpad) and the disposable traversal script were
both deleted immediately after this report was written. Nothing from the
fixture (the `CONTROLLED-TEST` records, the changed docstring, the
snapshot, the context packet, the doc page) exists anywhere in either
repository's tracked tree, before or after this demonstration.
