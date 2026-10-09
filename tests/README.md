# tests/

One test module per `src/codecompass/` module at minimum, run via
`pytest` (`pyproject.toml`'s `testpaths = ["tests"]`) — count the
`test_*.py` files directly for the current total rather than trusting a
number here, since it grows with every phase and would otherwise go
stale the moment this file isn't updated alongside it. `tests/fixtures/`
holds shared, hand-written input fixtures (sample manifests, lock files,
a small real demo project) used across several test modules rather than
duplicated per-module.

Maintainer-only scripts under `scripts/` (not part of the `codecompass`
package) have their own test modules here too
(e.g. `test_prepare_cleanroom_branch.py`, `test_cleanroom_broker.py`).
