# tests/

No package exists yet (see
[`planning/phase-0-repo-scaffolding.md`](../planning/phase-0-repo-scaffolding.md)).
Real tests begin in Phase 1 alongside `src/codecompass/`, mirroring its
module structure with one test module per source module minimum.

This directory exists now so `pyproject.toml`'s `testpaths` and future CI
wiring (Phase 6) have a stable target from commit one. It intentionally
contains no placeholder test files — an empty `assert True` test would
give a false-green signal with nothing to verify.
