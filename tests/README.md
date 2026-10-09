# tests/

895 tests across 39 modules, one test module per `src/codecompass/`
module at minimum, run via `pytest` (`pyproject.toml`'s `testpaths =
["tests"]`). `tests/fixtures/` holds shared, hand-written input fixtures
(sample manifests, lock files, a small real demo project) used across
several test modules rather than duplicated per-module.

Maintainer-only scripts under `scripts/` (not part of the `codecompass`
package) have their own test modules here too
(e.g. `test_prepare_cleanroom_branch.py`, `test_cleanroom_broker.py`).
