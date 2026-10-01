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


def test_deleting_the_current_maximum_id_does_not_reuse_it(tmp_path, monkeypatch):
    """The actual regression test for the bug documented at
    planning/knowledge/assertions/id-reuse-001.md: the original
    `max(current ids) + 1` implementation reused a deleted task's id
    specifically when that task held the current maximum, even with
    older tasks still present. Neither pre-existing test above exercises
    this -- the first only deletes the non-maximum id."""
    monkeypatch.chdir(tmp_path)
    tinytodo.STORE_PATH = Path("todo.json")
    a = tinytodo.add("first")
    b = tinytodo.add("second")
    c = tinytodo.add("third")
    assert (a.id, b.id, c.id) == (1, 2, 3)
    tinytodo.delete(c.id)  # delete the current MAXIMUM, not a lower one
    d = tinytodo.add("fourth")
    assert d.id == 4, "the deleted maximum id must not be reused"
    assert [t.id for t in tinytodo.list_tasks()] == [1, 2, 4]


def test_persisted_counter_survives_a_second_max_delete_cycle(tmp_path, monkeypatch):
    """Guards against a fix that merely happens to avoid reuse once by
    coincidence rather than via a real, persisted high-water-mark."""
    monkeypatch.chdir(tmp_path)
    tinytodo.STORE_PATH = Path("todo.json")
    a = tinytodo.add("a")
    b = tinytodo.add("b")
    tinytodo.delete(b.id)
    c = tinytodo.add("c")
    assert c.id == 3
    tinytodo.delete(c.id)
    d = tinytodo.add("d")
    assert d.id == 4, "the counter must keep advancing across repeated max-deletes"
    assert [t.id for t in tinytodo.list_tasks()] == [1, 4]


def test_counter_is_durable_across_a_fresh_process_reload(tmp_path, monkeypatch):
    """Guards against an in-memory-only counter that isn't actually
    persisted to todo.json."""
    monkeypatch.chdir(tmp_path)
    tinytodo.STORE_PATH = Path("todo.json")
    tinytodo.add("a")
    b = tinytodo.add("b")
    tinytodo.delete(b.id)
    # Simulate a fresh process: re-read everything from disk, trusting
    # nothing held in this test's own Python-level variables.
    next_id, tasks = tinytodo._load_store()
    assert next_id == 3, "the persisted counter itself must already be 3 on disk"
    e = tinytodo.add("e")
    assert e.id == 3
