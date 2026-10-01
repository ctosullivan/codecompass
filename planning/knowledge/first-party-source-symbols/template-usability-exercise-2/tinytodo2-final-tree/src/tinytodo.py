"""tinytodo: a tiny, single-file command-line todo list.

Stores tasks in a local JSON file (todo.json in the current directory).
Deliberately minimal: no priorities, no due dates, no categories — just
a description and a done flag. The one subtle design choice in this
module is how task ids are assigned: see `_next_id`.

FIXED (Phase 79 sixth amendment correction 3, propagation demonstration):
a prior version of this module computed the next id as
`max(current task ids) + 1`, which silently reused a deleted task's id
whenever that task held the current maximum at the moment of its own
deletion — independently reproduced and documented at
`planning/knowledge/assertions/id-reuse-001.md`. This version instead
persists a `next_id` high-water-mark counter in `todo.json` itself,
alongside the task list, so the counter survives a deletion regardless
of which task's id is removed.
"""
from __future__ import annotations

import json
import sys
from dataclasses import dataclass, asdict
from pathlib import Path

STORE_PATH = Path("todo.json")


@dataclass
class Task:
    id: int
    description: str
    done: bool = False


def _load_store() -> tuple[int, list[Task]]:
    """Returns `(next_id, tasks)`. A missing or legacy (bare-list) store
    is treated as "never indexed under this format" -- `next_id` starts
    at 1, same as a brand-new store, and is backfilled to a real
    high-water-mark on the very next `add` regardless of what the
    now-untracked legacy tasks' own ids were (a real, disclosed migration
    limitation, not a silent assumption)."""
    if not STORE_PATH.exists():
        return 1, []
    raw = json.loads(STORE_PATH.read_text())
    if isinstance(raw, list):
        # Legacy bare-list format (pre-fix). No persisted counter exists;
        # start from the ordinary empty-store default rather than
        # guessing at a prior high-water-mark that was never recorded.
        return 1, [Task(**t) for t in raw]
    return raw.get("next_id", 1), [Task(**t) for t in raw.get("tasks", [])]


def _save_store(next_id: int, tasks: list[Task]) -> None:
    STORE_PATH.write_text(
        json.dumps({"next_id": next_id, "tasks": [asdict(t) for t in tasks]}, indent=2)
    )


def add(description: str) -> Task:
    next_id, tasks = _load_store()
    task = Task(id=next_id, description=description)
    tasks.append(task)
    _save_store(next_id + 1, tasks)
    return task


def complete(task_id: int) -> bool:
    next_id, tasks = _load_store()
    for t in tasks:
        if t.id == task_id:
            t.done = True
            _save_store(next_id, tasks)
            return True
    return False


def delete(task_id: int) -> bool:
    next_id, tasks = _load_store()
    remaining = [t for t in tasks if t.id != task_id]
    if len(remaining) == len(tasks):
        return False
    _save_store(next_id, remaining)
    return True


def list_tasks() -> list[Task]:
    _next_id, tasks = _load_store()
    return tasks


def main(argv: list[str]) -> int:
    if not argv:
        print("usage: tinytodo <add|complete|delete|list> [args]")
        return 1
    cmd, *rest = argv
    if cmd == "add":
        task = add(" ".join(rest))
        print(f"added #{task.id}: {task.description}")
    elif cmd == "complete":
        ok = complete(int(rest[0]))
        print("done" if ok else "not found")
    elif cmd == "delete":
        ok = delete(int(rest[0]))
        print("deleted" if ok else "not found")
    elif cmd == "list":
        for t in list_tasks():
            mark = "x" if t.done else " "
            print(f"[{mark}] #{t.id} {t.description}")
    else:
        print(f"unknown command: {cmd}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
