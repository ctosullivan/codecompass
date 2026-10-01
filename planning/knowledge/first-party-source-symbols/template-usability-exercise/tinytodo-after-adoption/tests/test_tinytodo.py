import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

import tinytodo  # noqa: E402


def test_ids_are_never_reused_after_delete(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    tinytodo.STORE_PATH = Path("todo.json")
    a = tinytodo.add("first")
    b = tinytodo.add("second")
    assert a.id == 1
    assert b.id == 2
    tinytodo.delete(a.id)
    c = tinytodo.add("third")
    assert c.id == 3, "a deleted task's id must never be reassigned"


def test_fresh_store_starts_at_one(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    tinytodo.STORE_PATH = Path("todo.json")
    a = tinytodo.add("only task")
    assert a.id == 1
