"""tinytodo: a tiny, single-file command-line todo list.

Stores tasks in a local JSON file (todo.json in the current directory).
Deliberately minimal: no priorities, no due dates, no categories — just
a description and a done flag. The one subtle design choice in this
module is how task ids are assigned: see `_next_id`.
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


def _load() -> list[Task]:
    if not STORE_PATH.exists():
        return []
    raw = json.loads(STORE_PATH.read_text())
    return [Task(**t) for t in raw]


def _save(tasks: list[Task]) -> None:
    STORE_PATH.write_text(json.dumps([asdict(t) for t in tasks], indent=2))


def _next_id(tasks: list[Task]) -> int:
    """Task ids are never reused, even after a task is deleted.

    The next id is always one more than the highest id *ever* assigned,
    not one more than the highest id *currently present*. A deleted
    task's old id is permanently retired. This matters because a
    completed task's id is sometimes referenced in external notes
    (commit messages, chat logs) before it's deleted — reusing that id
    for a brand-new, unrelated task would make an old reference
    ambiguous. The tradeoff: ids are not a dense 1..N sequence once any
    task has ever been deleted, and the module has no record of "highest
    id ever assigned" beyond what's visible in the current task list, so
    in practice the guarantee only holds within a single todo.json's own
    continuous history -- deleting every task and starting fresh resets
    the counter to 0, because there's nothing left to infer the prior
    high-water mark from.
    """
    if not tasks:
        return 1
    return max(t.id for t in tasks) + 1


def add(description: str) -> Task:
    tasks = _load()
    task = Task(id=_next_id(tasks), description=description)
    tasks.append(task)
    _save(tasks)
    return task


def complete(task_id: int) -> bool:
    tasks = _load()
    for t in tasks:
        if t.id == task_id:
            t.done = True
            _save(tasks)
            return True
    return False


def delete(task_id: int) -> bool:
    tasks = _load()
    remaining = [t for t in tasks if t.id != task_id]
    if len(remaining) == len(tasks):
        return False
    _save(remaining)
    return True


def list_tasks() -> list[Task]:
    return _load()


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
