"""Tests for scripts/cleanroom_prompt_assembler.py -- Phase 81B
Amendment 4 (planning/phase-81b-clean-room-redocumentation.md §26).
Imported directly from its file path, matching this project's own
existing precedent for maintainer-only scripts.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

_SCRIPT_PATH = Path(__file__).resolve().parent.parent / "scripts" / "cleanroom_prompt_assembler.py"
_spec = importlib.util.spec_from_file_location("cleanroom_prompt_assembler", _SCRIPT_PATH)
assembler = importlib.util.module_from_spec(_spec)
sys.modules["cleanroom_prompt_assembler"] = assembler
_spec.loader.exec_module(assembler)


def test_assembles_files_of_every_real_extension_in_the_handoff(tmp_path):
    """Regression test for a real cold-reader finding (fifth pass): a
    fixed suffix allow-list previously used here silently dropped real
    evidence content (.hs Haskell source, .cabal/.lock build files,
    .gitmodules) the moment prepare_cleanroom_branch.py's own
    ALLOW_PATHS grew to cover new file types -- the two lists drifted
    independently. Every text file must now be included regardless of
    its extension."""
    samples = {
        "module.hs": "module Adapter.Scanner where\n",
        "pkg.cabal": "name: codecompass-adaptor-haskell\n",
        "stack.yaml.lock": "packages: []\n",
        ".gitmodules": '[submodule "x"]\n\tpath = x\n',
        "readme.md": "# hi\n",
        "script.py": "print('hi')\n",
        "config.toml": "a = 1\n",
    }
    for name, content in samples.items():
        (tmp_path / name).write_text(content, encoding="utf-8")

    blob = assembler.assemble_evidence_blob(tmp_path)
    for name, content in samples.items():
        assert f"=== EVIDENCE FILE: {name} ===" in blob, f"{name} missing from assembled blob"
        assert content.strip() in blob


def test_skips_binary_files_without_crashing(tmp_path):
    (tmp_path / "data.db").write_bytes(b"\xff\xfe\x00\x01binary-garbage\x00\xff")
    (tmp_path / "real.py").write_text("x = 1\n", encoding="utf-8")

    blob = assembler.assemble_evidence_blob(tmp_path)
    assert "=== EVIDENCE FILE: real.py ===" in blob
    assert "data.db" not in blob


def test_skips_pycache_and_stack_work_directories(tmp_path):
    (tmp_path / "__pycache__").mkdir()
    (tmp_path / "__pycache__" / "mod.pyc").write_bytes(b"\x00\x01")
    (tmp_path / ".stack-work").mkdir()
    (tmp_path / ".stack-work" / "garbage.txt").write_text("x", encoding="utf-8")
    (tmp_path / "real.py").write_text("x = 1\n", encoding="utf-8")

    blob = assembler.assemble_evidence_blob(tmp_path)
    assert "real.py" in blob
    assert "mod.pyc" not in blob
    assert "garbage.txt" not in blob
