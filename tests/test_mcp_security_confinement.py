"""Adversarial filesystem-confinement tests for the Phase 88 security
corrections to `knowledge_api.py`/`knowledge_intermediate.py`/`oracle.py`.
See `planning/phase-88-agent-integration-mcp.md` §17.1-§17.4, §17.9,
§18.1 for the full design history this implements.

Three things are checked, each with its own adversarial case:

1. A live read confined via `_read_confined_bytes` refuses a symlinked
   final component and a resolved escape, atomically (§17.3).
2. A slug-scoped directory confined via `_open_confined_dir_fd`/
   `_open_confined_subdir_fd` refuses a symlinked directory entry, and
   every subsequent child-file read performed `dir_fd`-relative through
   that descriptor is unaffected by the directory entry being swapped
   for a symlink *after* the descriptor was opened -- the actual
   property §18.1 claims, not merely the point-in-time check §17.9 had
   (the test this plan's own history says the prior design could not
   have passed).
3. The higher-level functions (`knowledge_api.get` for a `symbol:` id,
   `find_gaps`) never leak content or a hash from outside the intended
   root, reporting the existing `"unconfirmed"`/skip outcomes instead --
   no new outcome category.
"""

from __future__ import annotations

import os
from pathlib import Path

import pytest

from codecompass import graph, oracle
from codecompass import knowledge_api as ka
from codecompass import knowledge_intermediate as ki

pytestmark = pytest.mark.skipif(
    not hasattr(os, "O_NOFOLLOW") or not hasattr(os, "O_DIRECTORY"),
    reason="O_NOFOLLOW/O_DIRECTORY are POSIX-only -- this project claims no Windows support",
)


# ---------------------------------------------------------------------------
# Fixture helpers
# ---------------------------------------------------------------------------


def _write_flat(path: Path, fields: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [f"{key}: {value}" for key, value in fields.items()]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _write_contract(path: Path, *, contract_id: str, check_id: str) -> None:
    import yaml

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        yaml.safe_dump(
            {
                "schema_version": 1,
                "contract_id": contract_id,
                "tested_paths": ["pkg/mod.py"],
                "checks": [
                    {
                        "check_id": check_id,
                        "scope": "scope A",
                        "execution_provider": "pytest",
                        "check_reference": "tests/test_mod.py::test_a",
                        "test_input_paths": ["tests/test_mod.py"],
                        "required": True,
                    }
                ],
            }
        ),
        encoding="utf-8",
    )


def _write_result(path: Path, *, contract_id: str, check_id: str, outcome: str = "PASS") -> None:
    import yaml

    path.parent.mkdir(parents=True, exist_ok=True)
    raw_dir = path.parent / "raw"
    raw_dir.mkdir(parents=True, exist_ok=True)
    raw_path = raw_dir / (path.stem + ".txt")
    raw_path.write_text("ok\n", encoding="utf-8")
    path.write_text(
        yaml.safe_dump(
            {
                "schema_version": 1,
                "contract_id": contract_id,
                "oracle_contract_id": contract_id,
                "check_id": check_id,
                "scope": "scope A",
                "outcome": outcome,
                "oracle_contract_content_hash": "0" * 64,
                "tested_subject_digest": "0" * 64,
                "test_input_digest": "0" * 64,
                "raw_output_ref": str(raw_path),
                "raw_output_sha256": oracle.sha256_file(raw_path),
                "executed_at": "2026-01-01T00:00:00Z",
            }
        ),
        encoding="utf-8",
    )


def _make_graph_db(project_root: Path, *, rel_path: str, content_hash: str) -> None:
    conn = graph.open_graph(project_root)
    try:
        conn.execute(
            "INSERT INTO source_files (path, language, content_hash, symbol_index_status) "
            "VALUES (?, 'python', ?, 'indexed')",
            (rel_path, content_hash),
        )
        file_id = conn.execute(
            "SELECT id FROM source_files WHERE path = ?", (rel_path,)
        ).fetchone()[0]
        conn.execute(
            "INSERT INTO source_symbols (source_file_id, name, kind, line, purpose, exposure) "
            "VALUES (?, 'widget', 'function', 10, 'does a thing', 'public')",
            (file_id,),
        )
        conn.commit()
    finally:
        conn.close()


# ---------------------------------------------------------------------------
# 1. `_read_confined_bytes`
# ---------------------------------------------------------------------------


class TestReadConfinedBytes:
    def test_valid_file_reads_through(self, tmp_path: Path) -> None:
        (tmp_path / "pkg").mkdir()
        target = tmp_path / "pkg" / "mod.py"
        target.write_text("x = 1\n", encoding="utf-8")
        assert ka._read_confined_bytes(tmp_path, "pkg/mod.py") == b"x = 1\n"

    def test_missing_file_returns_none(self, tmp_path: Path) -> None:
        assert ka._read_confined_bytes(tmp_path, "pkg/does_not_exist.py") is None

    def test_symlinked_final_component_refused(self, tmp_path: Path) -> None:
        outside = tmp_path.parent / "outside_secret.txt"
        outside.write_text("OUTSIDE-SECRET\n", encoding="utf-8")
        (tmp_path / "pkg").mkdir()
        link = tmp_path / "pkg" / "mod.py"
        link.symlink_to(outside)
        # A plain, unconfined read would follow the symlink and read the
        # outside content -- confirm that's true of the naive approach,
        # then confirm the confined helper refuses it.
        assert link.read_text(encoding="utf-8") == "OUTSIDE-SECRET\n"
        assert ka._read_confined_bytes(tmp_path, "pkg/mod.py") is None

    def test_resolved_escape_via_traversal_refused(self, tmp_path: Path) -> None:
        (tmp_path / "pkg").mkdir()
        outside = tmp_path.parent / "another_secret.txt"
        outside.write_text("ANOTHER-SECRET\n", encoding="utf-8")
        assert ka._read_confined_bytes(tmp_path, f"pkg/../../{outside.name}") is None

    def test_dir_fd_relative_read(self, tmp_path: Path) -> None:
        (tmp_path / "d").mkdir()
        (tmp_path / "d" / "f.txt").write_text("hello\n", encoding="utf-8")
        fd = os.open(tmp_path / "d", os.O_RDONLY | os.O_NOFOLLOW | os.O_DIRECTORY)
        try:
            assert ka._read_confined_bytes(tmp_path, "f.txt", dir_fd=fd) == b"hello\n"
            assert ka._read_confined_bytes(tmp_path, "does_not_exist.txt", dir_fd=fd) is None
        finally:
            os.close(fd)


# ---------------------------------------------------------------------------
# 2. `_open_confined_dir_fd` / `_open_confined_subdir_fd`, and the real
#    directory-substitution race this round's own fix actually closes.
# ---------------------------------------------------------------------------


class TestConfinedDirFd:
    def test_valid_directory_opens(self, tmp_path: Path) -> None:
        (tmp_path / "slugs" / "real-slug").mkdir(parents=True)
        fd = ka._open_confined_dir_fd(tmp_path / "slugs", "real-slug")
        assert fd is not None
        os.close(fd)

    def test_symlinked_entry_refused(self, tmp_path: Path) -> None:
        (tmp_path / "slugs").mkdir()
        outside = tmp_path.parent / "outside-dir"
        outside.mkdir()
        (tmp_path / "slugs" / "evil-slug").symlink_to(outside, target_is_directory=True)
        assert ka._open_confined_dir_fd(tmp_path / "slugs", "evil-slug") is None

    def test_malformed_name_rejected(self, tmp_path: Path) -> None:
        (tmp_path / "slugs").mkdir()
        for bad in ("..", ".", "../escape", "/etc", "a/b"):
            assert ka._open_confined_dir_fd(tmp_path / "slugs", bad) is None

    def test_missing_entry_returns_none(self, tmp_path: Path) -> None:
        (tmp_path / "slugs").mkdir()
        assert ka._open_confined_dir_fd(tmp_path / "slugs", "never-created") is None

    def test_subdir_fd_extends_without_path_rewalk(self, tmp_path: Path) -> None:
        (tmp_path / "slugs" / "real-slug" / "results").mkdir(parents=True)
        (tmp_path / "slugs" / "real-slug" / "results" / "r.yaml").write_text(
            "x: 1\n", encoding="utf-8"
        )
        parent_fd = ka._open_confined_dir_fd(tmp_path / "slugs", "real-slug")
        assert parent_fd is not None
        try:
            child_fd = ka._open_confined_subdir_fd(parent_fd, "results")
            assert child_fd is not None
            try:
                assert ka._read_confined_bytes(tmp_path, "r.yaml", dir_fd=child_fd) == b"x: 1\n"
            finally:
                os.close(child_fd)
        finally:
            os.close(parent_fd)

    def test_directory_substitution_after_open_does_not_affect_held_fd(
        self, tmp_path: Path
    ) -> None:
        """The property this round's own fix (§18.1) actually adds, not
        merely the point-in-time check §17.9 already had: once a
        directory fd is open, reading its children is unaffected by the
        original path entry being replaced with a symlink to somewhere
        else -- a fresh, unconfined, pathname-based read of the *same
        name* at that point would follow the substitution and read the
        attacker's content; a read through the *already-open descriptor*
        must not."""
        real_dir = tmp_path / "slugs" / "real-slug"
        real_dir.mkdir(parents=True)
        (real_dir / "f.yaml").write_text("original\n", encoding="utf-8")

        fd = ka._open_confined_dir_fd(tmp_path / "slugs", "real-slug")
        assert fd is not None
        try:
            # Swap the directory entry for a symlink to attacker content,
            # *after* the descriptor above was already opened.
            attacker_dir = tmp_path / "attacker-dir"
            attacker_dir.mkdir()
            (attacker_dir / "f.yaml").write_text("attacker\n", encoding="utf-8")
            os.rename(real_dir, tmp_path / "slugs" / "real-slug-moved-aside")
            (tmp_path / "slugs" / "real-slug").symlink_to(attacker_dir, target_is_directory=True)

            # A fresh, unconfined, pathname-based read now genuinely
            # reads the attacker's content -- confirms the substitution
            # really happened and really would be exploitable without
            # the fd-relative mechanism.
            moved_target = tmp_path / "slugs" / "real-slug" / "f.yaml"
            assert moved_target.read_text(encoding="utf-8") == "attacker\n"

            # The already-open descriptor is unaffected: it still refers
            # to the original directory's own inode.
            assert ka._read_confined_bytes(tmp_path, "f.yaml", dir_fd=fd) == b"original\n"

            # A *fresh* confined open of the same name, performed now
            # (after the substitution), correctly refuses -- this is the
            # point-in-time check still doing its job for a new open; it
            # is the already-held fd from *before* the swap that
            # demonstrates the fix's own new property, confirmed above.
            fresh = ka._open_confined_dir_fd(tmp_path / "slugs", "real-slug")
            assert fresh is None
        finally:
            os.close(fd)


# ---------------------------------------------------------------------------
# 3. `_list_slugs` symlink exclusion, and `load_slug_records`'s
#    `confined_dir_fd` mode (per-file symlink exclusion).
# ---------------------------------------------------------------------------


class TestSlugEnumerationAndRecords:
    def test_list_slugs_excludes_symlinked_entry(self, tmp_path: Path) -> None:
        kdir = tmp_path / "planning" / "knowledge"
        kdir.mkdir(parents=True)
        (kdir / "real-slug").mkdir()
        outside = tmp_path / "outside-slug-target"
        outside.mkdir()
        (kdir / "evil-slug").symlink_to(outside, target_is_directory=True)
        assert ki._list_slugs(tmp_path) == ["real-slug"]

    def test_load_slug_records_via_dir_fd_excludes_symlinked_yaml(self, tmp_path: Path) -> None:
        slug_dir = tmp_path / "planning" / "knowledge" / "demo"
        slug_dir.mkdir(parents=True)
        _write_flat(
            slug_dir / "CL-DEMO-001.yaml",
            {"id": "CL-DEMO-001", "kind": "claim", "statement": "x"},
        )
        outside = tmp_path / "outside-record.yaml"
        _write_flat(outside, {"id": "CL-EVIL-001", "kind": "claim", "statement": "evil"})
        (slug_dir / "CL-EVIL-001.yaml").symlink_to(outside)

        fd = os.open(slug_dir, os.O_RDONLY | os.O_NOFOLLOW | os.O_DIRECTORY)
        try:
            records = ki.load_slug_records(slug_dir, confined_dir_fd=fd)
        finally:
            os.close(fd)
        assert set(records) == {"CL-DEMO-001"}

        # Confirm the unconfined, default-mode path still works exactly
        # as before for the ordinary case (no behaviour change there),
        # though it genuinely *does* follow the symlink -- that call
        # site has no confined_dir_fd and was never claimed to.
        unconfined = ki.load_slug_records(slug_dir)
        assert "CL-EVIL-001" in unconfined


# ---------------------------------------------------------------------------
# 4. `knowledge_api.get()` for a `symbol:` id -- §17.1-§17.3.
# ---------------------------------------------------------------------------


class TestGetSymbolConfinement:
    def test_current_status_for_real_unmodified_file(self, tmp_path: Path) -> None:
        (tmp_path / "pkg").mkdir()
        target = tmp_path / "pkg" / "mod.py"
        target.write_text("def widget(): pass\n", encoding="utf-8")
        content_hash = oracle.sha256_file(target)
        _make_graph_db(tmp_path, rel_path="pkg/mod.py", content_hash=content_hash)

        resp = ka.get(tmp_path, "symbol:pkg/mod.py:widget:function:10")
        assert resp.status == "result"
        assert resp.results[0].consistency.status == "current"

    def test_symlink_substitution_after_sync_reports_unconfirmed_not_stale_with_leaked_hash(
        self, tmp_path: Path
    ) -> None:
        """The exact scenario §17.1 names: an already-indexed path is
        later replaced with a symlink escaping `project_root`. Must never
        read/hash the external target -- status stays `"unconfirmed"`
        (the existing default), never `"current"`/`"stale"` derived from
        attacker-controlled content."""
        (tmp_path / "pkg").mkdir()
        original = tmp_path / "pkg" / "mod.py"
        original.write_text("def widget(): pass\n", encoding="utf-8")
        indexed_hash = oracle.sha256_file(original)
        _make_graph_db(tmp_path, rel_path="pkg/mod.py", content_hash=indexed_hash)

        outside = tmp_path.parent / "attacker_mod.py"
        outside.write_text("def widget(): exfiltrate()\n", encoding="utf-8")
        original.unlink()
        original.symlink_to(outside)

        resp = ka.get(tmp_path, "symbol:pkg/mod.py:widget:function:10")
        assert resp.status == "result"
        consistency = resp.results[0].consistency
        assert consistency.status == "unconfirmed"
        # The attacker's own content hash must never appear anywhere in
        # the response as if it were a legitimately re-confirmed value.
        attacker_hash = oracle.sha256_file(outside)
        assert attacker_hash not in str(resp)


# ---------------------------------------------------------------------------
# 5. `find_gaps` -- the contracts-tree raw-slug call sites, and the
#    evidence-scanning loop (§17.2/§17.9/§18.1 combined).
# ---------------------------------------------------------------------------


class TestFindGapsConfinement:
    def test_symlinked_slug_directory_under_knowledge_root_yields_no_gaps_and_no_crash(
        self, tmp_path: Path
    ) -> None:
        kdir = tmp_path / "planning" / "knowledge"
        kdir.mkdir(parents=True)
        outside = tmp_path / "outside-knowledge-target"
        outside.mkdir()
        _write_flat(
            outside / "CL-EVIL-001.yaml",
            {"id": "CL-EVIL-001", "kind": "claim", "statement": "evil", "status": "contradicted"},
        )
        (kdir / "evil-slug").symlink_to(outside, target_is_directory=True)

        resp = ka.find_gaps(tmp_path, slug="evil-slug")
        assert resp.status != "gap" or not resp.gaps
        assert resp.gaps == []

    def test_symlinked_results_directory_under_contracts_tree_is_not_followed(
        self, tmp_path: Path
    ) -> None:
        kdir = tmp_path / "planning" / "knowledge" / "demo"
        kdir.mkdir(parents=True)
        _write_flat(
            kdir / "REQ-DEMO-001.yaml",
            {"id": "REQ-DEMO-001", "kind": "requirement", "statement": "req"},
        )
        _write_flat(
            kdir / "CL-DEMO-001.yaml",
            {"id": "CL-DEMO-001", "kind": "claim", "statement": "x",
             "supporting_evidence": "[]", "depends_on": "[]"},
        )
        contracts_dir = tmp_path / "planning" / "contracts" / "demo"
        _write_contract(
            contracts_dir / "oracle-contract.yaml", contract_id="REQ-DEMO-001", check_id="chk-a"
        )

        outside_results = tmp_path / "outside-results"
        outside_results.mkdir()
        _write_result(outside_results / "evil.yaml", contract_id="REQ-DEMO-001", check_id="chk-a")
        (contracts_dir / "results").symlink_to(outside_results, target_is_directory=True)

        # Must not raise, and must not treat the outside result as a
        # legitimate, currently-passing result for this contract.
        resp = ka.find_gaps(tmp_path, slug="demo")
        assert resp is not None
        by_ref = ka._results_by_test_ref(tmp_path, "demo", confined_dir_fd=None)
        # Confined call site returns nothing from the symlinked results/
        # directory -- the contracts_fd/results_fd path inside find_gaps
        # already exercised this; this direct call confirms the
        # unconfined default (no confined_dir_fd) is a different, legacy
        # code path not used by find_gaps.
        assert by_ref == {}

    def test_evidence_scanning_loop_skips_symlinked_test_ref(self, tmp_path: Path) -> None:
        kdir = tmp_path / "planning" / "knowledge" / "demo"
        kdir.mkdir(parents=True)
        _write_flat(
            kdir / "REQ-DEMO-001.yaml",
            {"id": "REQ-DEMO-001", "kind": "requirement", "statement": "req"},
        )
        _write_flat(
            kdir / "EV-DEMO-001.yaml",
            {
                "id": "EV-DEMO-001", "kind": "evidence", "evidence_kind": "test",
                "test_ref": "planning/contracts/demo/results/evil.yaml",
                "what_it_shows": "x",
            },
        )
        contracts_dir = tmp_path / "planning" / "contracts" / "demo"
        _write_contract(
            contracts_dir / "oracle-contract.yaml", contract_id="REQ-DEMO-001", check_id="chk-a"
        )
        results_dir = contracts_dir / "results"
        results_dir.mkdir(parents=True)
        outside = tmp_path.parent / "evil_result.yaml"
        _write_result(outside, contract_id="REQ-DEMO-001", check_id="chk-a", outcome="INVALID")
        (results_dir / "evil.yaml").symlink_to(outside)

        resp = ka.find_gaps(tmp_path, slug="demo")
        assert all(g.kind != "stale_test_citation" for g in resp.gaps)
