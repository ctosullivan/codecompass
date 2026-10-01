# Learnings

A running log of candidates (see this directory's own `README.md` for
the lifecycle). One entry per candidate; update its own status in place
once reviewed rather than duplicating it.

---

## 2026-10-01 — `_next_id`'s delete-everything caveat has no regression test

**What happened**: while writing up `_next_id`'s id-reuse design as an
assertion (`planning/knowledge/assertions/task-ids-001.md`), the existing
test suite (`tests/test_tinytodo.py`) turned out to cover "id not reused
while another task survives" but not the docstring's own stated caveat
("deleting every task and starting fresh resets the counter to 0
[in practice: to 1]"). Confirmed by hand that the caveat is real (delete
both existing tasks, add a new one, its id came back as `1`), but nothing
in the committed test suite would catch a future change that broke this
specific behavior.

**Evidence**: `src/tinytodo.py:36-55` (the docstring making the claim);
`tests/test_tinytodo.py` (both tests, neither empties the list); manual
`python3 -c` check on 2026-10-01 reproducing the reset.

**Why it seems worth keeping**: a documented design caveat with no test
behind it is exactly the kind of thing that silently breaks in a later
refactor and isn't noticed until someone's old task-id reference goes
ambiguous again — the whole reason the design exists.

**Status**: candidate, not yet reviewed. Likely promotion: a new test,
`test_id_resets_after_deleting_every_task`, added to
`tests/test_tinytodo.py`. Not added as part of this documentation
exercise since writing tests wasn't the task at hand — left here instead
of silently added, per this project's own `CLAUDE.md` §5.
