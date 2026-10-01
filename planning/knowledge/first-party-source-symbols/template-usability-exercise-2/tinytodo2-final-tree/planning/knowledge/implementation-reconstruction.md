# tinytodo — implementation reconstruction (model-blind, as-built)

Source evidence: exactly two files supplied in this export —
`src/tinytodo.py` (114 lines) and `tests/test_tinytodo.py` (25 lines).
No other file, documentation, ADR, or prior conceptual model was consulted.
All claims below are either read directly from these two files or
produced by executing the real code in a scratch directory during this
session (shown verbatim).

## 1. Modules

Single-file module, no package structure: `tinytodo.py`. It has exactly
one responsibility: a minimal CLI todo list backed by a flat JSON file.
Internal organization within the one file:

- A `Task` dataclass (the data model).
- Two private I/O helpers, `_load`/`_save` (persistence).
- One private helper, `_next_id` (id-assignment policy).
- Four public operations: `add`, `complete`, `delete`, `list_tasks`.
- One CLI dispatcher, `main(argv)`, plus a `__main__` guard calling
  `sys.exit(main(sys.argv[1:]))`.

There is no separate test-support module; `tests/test_tinytodo.py`
inserts `src/` onto `sys.path` manually and imports `tinytodo` directly
(no installed package, no `pyproject.toml`/`setup.py` present in this
export).

## 2. API / CLI surface

Public Python functions (all module-level, no classes besides the
`Task` dataclass):

- `add(description: str) -> Task` — loads the store, computes the next
  id via `_next_id`, appends a new `Task`, saves, returns it.
- `complete(task_id: int) -> bool` — loads, linear-scans for a task
  with matching `id`, sets `done = True` and saves if found (returns
  `True`); returns `False` without writing if not found.
- `delete(task_id: int) -> bool` — loads, filters out the matching
  task by id, saves only if the list actually shrank (returns
  `True`/`False` accordingly). Note: if two tasks somehow shared the
  same id, both would be removed in one call (filter, not single-match
  removal) — see Limitations.
- `list_tasks() -> list[Task]` — thin wrapper, just returns `_load()`.

CLI surface, driven entirely by `main(argv: list[str]) -> int`:

- `tinytodo add <words...>` → joins `rest` with single spaces as the
  description, prints `added #<id>: <description>`, returns 0.
- `tinytodo complete <id>` → prints `done` or `not found`, returns 0
  either way (exit code does not reflect success/failure of the
  operation itself, only of argument parsing getting far enough).
- `tinytodo delete <id>` → prints `deleted` or `not found`, returns 0.
- `tinytodo list` → prints one line per task, `[x]`/`[ ]` marker, `#id`,
  description.
- No args → prints a usage line, returns 1.
- Unknown command → prints `unknown command: <cmd>`, returns 1.

Confirmed by direct execution (`main(["add","buy","milk"])` etc. — see
§5 for the full transcript) that this is exactly what happens; the
`main` function contains no behavior beyond this dispatch table.

## 3. Data and persistence

`Task` is a `@dataclass` with three fields: `id: int`,
`description: str`, `done: bool = False`. No schema versioning, no
migrations, no separate id/sequence file.

Persistence is a single flat JSON array written to `STORE_PATH`
(module-level `Path("todo.json")`, relative to the current working
directory — there is no XDG/home-directory/config-dir path, no env var
override). `_load` returns `[]` if the file doesn't exist; otherwise it
does `json.loads(...)` and constructs `Task(**t)` for every element with
no validation beyond what `dataclass.__init__` enforces. `_save` writes
`json.dumps([asdict(t) for t in tasks], indent=2)`, i.e. it rewrites the
*entire* file on every mutating call (add/complete/delete) — there is no
incremental/append persistence and no locking.

Confirmed on disk (`todo.json` after add/complete/delete sequence):
```json
[
  {
    "id": 2,
    "description": "walk dog",
    "done": false
  }
]
```
This shows the whole-file-rewrite model directly — only the one
surviving task is present after a delete, with a clean `indent=2` JSON
array.

Also confirmed: a stored record missing the `done` key loads fine
(`Task(id=1, description='x', done=False)` — the dataclass default
fills it in), but a stored record with an *extra*, unrecognized key
(`"extra": 1`) raises `TypeError: Task.__init__() got an unexpected
keyword argument 'extra'` out of `_load`, uncaught. So `_load` is
forward-compatible with old/missing fields but not forward-compatible
with new/unknown ones, and any read of a hand-edited or
differently-versioned `todo.json` can crash the whole CLI.

## 4. Dependencies

Only the standard library: `json`, `sys`, `dataclasses`
(`dataclass`, `asdict`), `pathlib.Path`, plus `from __future__ import
annotations`. No third-party imports at all (no `typer`, no `click`, no
`rich` — this module does its own `print`-based CLI parsing by hand).
Nothing in this export's `tinytodo.py` touches the repository's vendored
dependencies listed elsewhere in project config; this topic's own code
has zero external dependencies.

## 5. Runtime paths (traced + executed)

Traced and then verified by direct execution of the real module (copied
nothing, imported `tinytodo` straight from the export's `src/` dir, ran
in a disposable temp cwd so `todo.json` didn't collide with anything):

```
rc= main(["add","buy","milk"])   -> prints "added #1: buy milk", rc 0
rc= main(["add","walk","dog"])   -> prints "added #2: walk dog", rc 0
rc= main(["list"])               -> "[ ] #1 buy milk" / "[ ] #2 walk dog"
rc= main(["complete","1"])       -> prints "done", rc 0
rc= main(["list"])               -> "[x] #1 buy milk" / "[ ] #2 walk dog"
rc= main(["delete","1"])         -> prints "deleted", rc 0
rc= main(["list"])               -> "[ ] #2 walk dog"
```

Call chain for `add`: `main` → `add` → `_load` → (`_next_id`) →
`Task(...)` → `tasks.append` → `_save`. For `complete`/`delete`: `main`
→ op → `_load` → in-place scan/filter → `_save` (only if a match was
found/removed) → return bool consumed by `main` purely for the
print branch, not for the exit code.

Also executed and confirmed:
- `main([])` → usage line, rc 1.
- `main(["frobnicate"])` → `unknown command: frobnicate`, rc 1.
- `main(["complete"])` / `main(["delete"])` with no id argument → both
  raise **uncaught `IndexError: list index out of range`** (from
  `rest[0]`) — the process would crash with a traceback, not a clean
  error message.
- `main(["complete","abc"])` → uncaught **`ValueError: invalid literal
  for int() with base 10: 'abc'`** — same story, no input validation
  before `int(rest[0])`.
- `add("")` (empty description, e.g. `tinytodo add` with no words)
  succeeds silently and stores a task with `description=''`.

## 6. Extension points

There is no plugin/registration mechanism of any kind. The only real
"extension point" visible in the code is the `if cmd == ...: elif ...`
chain inside `main` — adding a new subcommand means adding another
`elif` branch by hand, following the existing pattern (parse `rest`,
call a module-level function, print one of two fixed strings, return
0). No example of this being done exists in the export (only four
commands are present); this is inferred from the one existing pattern,
not confirmed by a second instance.

## 7. Build / configuration

No build or config file of any kind is present in this export (no
`pyproject.toml`, `setup.py`, `requirements.txt`, CLI entry-point
declaration, env vars, or config file read anywhere in `tinytodo.py`).
The only "configuration" in the code is the single module-level
constant `STORE_PATH = Path("todo.json")`, which the test suite
overrides directly by monkeypatching the attribute
(`tinytodo.STORE_PATH = Path("todo.json")` after `monkeypatch.chdir`) —
i.e. there is no supported configuration API for the storage location;
tests reach in and mutate module state directly.

## 8. Tests (bodies read directly, not inferred from names)

Two tests total, both using `tmp_path`/`monkeypatch` to isolate
`todo.json` per test:

- `test_ids_are_never_reused_after_delete`: adds two tasks (asserts
  ids 1 and 2), deletes the first, adds a third, and asserts the new
  task gets id **3**, with the explicit assertion message "a deleted
  task's id must never be reassigned."
- `test_fresh_store_starts_at_one`: adds a single task to a brand-new
  store and asserts its id is 1.

That is the entirety of the test suite — no test covers `complete`,
`list_tasks`, the CLI (`main`) at all, JSON persistence format, missing
fields, or any of the crash paths found in §5. Both existing tests only
exercise the specific "delete a non-max-id task, then add" case — they
do not test deleting the *current maximum*-id task, which is exactly
where the real behavior diverges most sharply from the stated
guarantee (see §9).

## 9. Limitations — what the evidence actually shows (docstring vs. code)

This is the central finding requested by the task brief. `_next_id`'s
docstring makes a strong, unqualified claim up front:

> "Task ids are never reused, even after a task is deleted. The next id
> is always one more than the highest id *ever* assigned, not one more
> than the highest id *currently present*."

The actual implementation is:
```python
def _next_id(tasks: list[Task]) -> int:
    if not tasks:
        return 1
    return max(t.id for t in tasks) + 1
```
This computes `max` over the ids **currently present**, i.e. exactly
the quantity the docstring says it is *not* doing. There is no stored
high-water mark, counter file, or any other record of ids that have
ever existed — the function's only input is the current in-memory
`tasks` list.

The docstring itself partially acknowledges a caveat ("deleting every
task and starting fresh resets the counter to 0"), but I confirmed by
direct execution that the real gap is substantially broader than that
disclosed caveat:

1. **Disclosed case, confirmed real**: delete the *only* task, add a
   new one → id resets to 1 (reuses the deleted task's id).
   ```
   a = add("a")        # a.id == 1
   delete(a.id)
   c = add("c")        # c.id == 1   <- reused, as the docstring admits
   ```

2. **Undisclosed case, confirmed real and more serious**: deleting the
   task that currently holds the *maximum* id — while other, older
   tasks still remain — causes the very next add to reuse that exact
   id, with no list-emptying involved at all:
   ```
   a = add("a"); b = add("b")   # a.id=1, b.id=2
   delete(b.id)                  # delete the max-id task; 'a' remains
   c = add("c")                  # c.id == 2  <-- REUSED b's id, confirmed by execution
   ```
   This directly reuses a previously-assigned, now-deleted task's id
   while the store is non-empty, which is exactly the scenario the
   docstring's headline claim ("ids are never reused, even after a task
   is deleted") says cannot happen, and it is not covered by the
   docstring's own "deleting every task" caveat (one other task, `a`,
   is still present throughout).

3. Generalizing this, confirmed: with ids `1,2,3` present, deleting
   both `2` and `3` and then adding reuses id `2` (the lower of the two
   deleted max-adjacent ids), again while task `1` still exists in the
   store — execution:
   ```
   a,b,d = add("a"), add("b"), add("d")   # ids 1,2,3
   delete(d.id); delete(b.id)             # delete 3, then 2
   e = add("e")                            # e.id == 2  <-- reused
   ```

4. The one case that genuinely does **not** reuse an id, confirmed by
   execution and matching both existing tests: deleting a task that is
   **not** the current maximum (e.g. delete the lowest id while a
   higher id remains) leaves `max()` unchanged, so the next id is
   correctly fresh (`delete` id 1 of `{1,2}` → next add gets `3`, not
   `1`). This is the *only* scenario the test suite actually exercises,
   which is why the much larger reuse hole in cases 2–3 is not caught
   by the existing tests.

**Bottom line**: the function's real guarantee is "the next id is one
more than the maximum id currently present in the store (or 1 if
empty)" — a simple `max()+1` scheme with no persistent high-water mark.
It reuses ids far more readily than its own docstring claims: any time
the task holding the current maximum id is deleted (not just "delete
everything"), the next `add` call will reissue that id. The docstring's
own disclosed caveat about emptying the store is real but describes
only the simplest special case of a much broader gap; the headline
sentence "ids are never reused, even after a task is deleted" is false
as a general statement about the code, confirmed by direct execution
rather than by reading alone.

Other, smaller gaps found directly in the code / by execution (not
docstring-related, but genuine unhandled cases):

- `main(["complete"])` / `main(["delete"])` with a missing id argument
  raise an uncaught `IndexError` — no argument-count validation.
- `main(["complete","abc"])` (non-numeric id) raises an uncaught
  `ValueError` from `int(rest[0])` — no input validation or
  try/except anywhere in `main`.
- `_load` has no handling for a `todo.json` containing a dict with an
  unexpected key; `Task(**t)` then raises `TypeError` and `list_tasks`/
  `add`/`complete`/`delete` all propagate it uncaught, since every one
  of them calls `_load` first. There is no schema check, no
  `try/except json.JSONDecodeError`, and no corruption recovery of any
  kind.
- `delete` removes *all* tasks matching `task_id` via a list
  comprehension filter rather than removing a single match; this is
  only an issue if the on-disk store ever contains duplicate ids (which
  nothing in the module prevents if the file is hand-edited), but as
  written it is a filter, not a find-and-remove-one.
- Exit codes from `main` do not distinguish "operation succeeded" vs.
  "operation reported not found" for `complete`/`delete` — both return
  0; only a missing/unknown command path returns 1.
- No concurrency protection at all: `_load`/`_save` is read-modify-write
  with no file locking, so two processes racing would silently lose one
  writer's update (last `_save` wins, whole file overwritten).
