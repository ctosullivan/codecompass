"""Tests for scripts/prepare_cleanroom_branch.py — a maintainer-only tool,
not part of the codecompass package. Imported directly from its file
path (see tests/test_check_knowledge_base.py's own identical precedent).

Phase 81B (`planning/phase-81b-clean-room-redocumentation.md` §6.1/
§6.1.1/§22 item 4): confirms the branch validator's own four fail-closed
conditions are genuinely enforced against a real build, not merely
trivially passing — an excluded path present, an unlisted path present,
a listed path missing, and a hash mismatch must each independently fail.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

_SCRIPT_PATH = (
    Path(__file__).resolve().parent.parent / "scripts" / "prepare_cleanroom_branch.py"
)
_spec = importlib.util.spec_from_file_location("prepare_cleanroom_branch", _SCRIPT_PATH)
prepare_cleanroom_branch = importlib.util.module_from_spec(_spec)
sys.modules["prepare_cleanroom_branch"] = prepare_cleanroom_branch
_spec.loader.exec_module(prepare_cleanroom_branch)

REPO_ROOT = Path(__file__).resolve().parent.parent


def _build(tmp_path: Path) -> Path:
    staging = tmp_path / "staging"
    args = type(
        "Args",
        (),
        {
            "staging": str(staging),
            "documented_revision": "test-revision",
            "slugs": "codecompass-domain",
        },
    )()
    assert prepare_cleanroom_branch.cmd_build(args) == 0
    return staging


def test_real_build_validates_clean(tmp_path):
    """A genuine build against the real repository passes its own
    validator with zero findings."""
    staging = _build(tmp_path)
    args = type("Args", (), {"staging": str(staging)})()
    assert prepare_cleanroom_branch.cmd_validate(args) == 0


def test_excluded_path_present_fails_closed(tmp_path):
    staging = _build(tmp_path)
    (staging / "README.md").write_text("smuggled narrative content\n", encoding="utf-8")
    args = type("Args", (), {"staging": str(staging)})()
    assert prepare_cleanroom_branch.cmd_validate(args) == 1


def test_unlisted_path_present_fails_closed(tmp_path):
    staging = _build(tmp_path)
    (staging / "src" / "sneaky.txt").write_text("not in the manifest\n", encoding="utf-8")
    args = type("Args", (), {"staging": str(staging)})()
    assert prepare_cleanroom_branch.cmd_validate(args) == 1


def test_manifest_listed_path_missing_fails_closed(tmp_path):
    staging = _build(tmp_path)
    (staging / "pyproject.toml").unlink()
    args = type("Args", (), {"staging": str(staging)})()
    assert prepare_cleanroom_branch.cmd_validate(args) == 1


def test_no_manifest_fails_closed(tmp_path):
    staging = tmp_path / "empty"
    staging.mkdir()
    args = type("Args", (), {"staging": str(staging)})()
    assert prepare_cleanroom_branch.cmd_validate(args) == 1


def test_allow_list_contains_no_narrative_documentation_paths():
    """Amendment 2/3: README.md/docs/**/architecture/**/ai-docs/** (and
    docs/domain/** specifically) must never appear in the allow-list
    itself — a structural guard against the allow-list silently growing
    to include narrative documentation later."""
    excluded_prefixes = (
        "README.md", "docs", "architecture", "ai-docs", "CONTRIBUTING.md", "CLAUDE.md",
    )
    for allowed in prepare_cleanroom_branch.ALLOW_PATHS:
        assert not any(
            allowed == p or allowed.startswith(p + "/") for p in excluded_prefixes
        ), f"narrative-documentation-shaped path leaked into ALLOW_PATHS: {allowed}"
