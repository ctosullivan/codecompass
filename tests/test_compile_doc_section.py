"""Tests for scripts/compile_doc_section.py (Phase 87 Stage 87A clean-
room section-compilation adapter, restructuring-pass amendment finding
B). See
planning/phase-87-documentation-schema-knowledge-compiled-documentation.md
§G.B for the corrected runtime-evidence-handoff design.

Mirrors tests/test_cleanroom_broker.py's own mocked-subprocess
convention -- never invokes real model inference in automated tests.
"""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
SCRIPT_PATH = ROOT / "scripts" / "compile_doc_section.py"

_spec = importlib.util.spec_from_file_location("compile_doc_section", SCRIPT_PATH)
cds = importlib.util.module_from_spec(_spec)
sys.modules["compile_doc_section"] = cds
_spec.loader.exec_module(cds)

sys.path.insert(0, str(ROOT / "src"))
from codecompass import doc_compiler as dc  # noqa: E402


def _packet(**overrides) -> dc.EvidencePacket:
    base = dict(
        section_id="s1",
        record_ids=["CL-DEMO-001"],
        hydrated={"CL-DEMO-001": {"statement": "demo statement", "status": "verified"}},
        serialized_chars=50,
    )
    base.update(overrides)
    return dc.EvidencePacket(**base)


# ---------------------------------------------------------------------------
# write_section_packet -- ephemeral, hash-verified staging (§G.B point 1)
# ---------------------------------------------------------------------------


def test_write_section_packet_creates_packet_and_manifest_with_content_hash(tmp_path):
    packet = _packet()
    packet_path, manifest_path = cds.write_section_packet(
        tmp_path, packet, schema_slug="demo-schema", source_revision="abc123",
    )
    assert packet_path.is_file()
    assert manifest_path.is_file()
    written = json.loads(packet_path.read_text(encoding="utf-8"))
    assert written["hydrated"]["CL-DEMO-001"]["statement"] == "demo statement"

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert manifest["section_id"] == "s1"
    assert manifest["source_revision"] == "abc123"
    assert manifest["schema_slug"] == "demo-schema"
    assert "content_sha256" in manifest and len(manifest["content_sha256"]) == 64


def test_write_section_packet_is_never_under_a_git_tracked_path(tmp_path):
    # §G.B's own correction: this must NEVER be a path git would ever
    # track (prepare_cleanroom_branch.py's own export mechanism reads
    # only from committed git objects -- a packet under a tracked path
    # risks a future contributor assuming it IS exported that way).
    packet = _packet()
    packet_path, _manifest_path = cds.write_section_packet(
        tmp_path, packet, schema_slug="demo-schema", source_revision="abc123",
    )
    assert not str(packet_path).startswith(str(tmp_path))  # ephemeral tempdir, outside the repo


# ---------------------------------------------------------------------------
# Integrity re-verification before use (§G.B point 2; Stage 87A test 4)
# ---------------------------------------------------------------------------


def test_verify_packet_integrity_passes_when_unaltered(tmp_path):
    packet = _packet()
    packet_path, manifest_path = cds.write_section_packet(
        tmp_path, packet, schema_slug="demo-schema", source_revision="abc123",
    )
    cds.verify_packet_integrity(packet_path, manifest_path)  # must not raise


def test_verify_packet_integrity_raises_when_altered_after_writing(tmp_path):
    packet = _packet()
    packet_path, manifest_path = cds.write_section_packet(
        tmp_path, packet, schema_slug="demo-schema", source_revision="abc123",
    )
    packet_path.write_text(packet_path.read_text(encoding="utf-8") + "tampered", encoding="utf-8")
    with pytest.raises(cds.CleanRoomAdapterError):
        cds.verify_packet_integrity(packet_path, manifest_path)


# ---------------------------------------------------------------------------
# Staging-directory content assertion (§G.B point 3; Stage 87A test 5)
# ---------------------------------------------------------------------------


def test_assert_staging_dir_contents_passes_for_exactly_packet_and_manifest(tmp_path):
    packet = _packet()
    packet_path, manifest_path = cds.write_section_packet(
        tmp_path, packet, schema_slug="demo-schema", source_revision="abc123",
    )
    cds.assert_staging_dir_contents(packet_path.parent, packet_path, manifest_path)  # no raise


def test_assert_staging_dir_contents_rejects_a_planted_extra_file(tmp_path):
    packet = _packet()
    packet_path, manifest_path = cds.write_section_packet(
        tmp_path, packet, schema_slug="demo-schema", source_revision="abc123",
    )
    (packet_path.parent / "sneaky-narrative.md").write_text("not evidence", encoding="utf-8")
    with pytest.raises(cds.CleanRoomAdapterError):
        cds.assert_staging_dir_contents(packet_path.parent, packet_path, manifest_path)


# ---------------------------------------------------------------------------
# Isolation preflight gating (§G.B point 4; Stage 87A test 6)
# ---------------------------------------------------------------------------


def test_run_isolation_preflight_raises_on_nonzero_exit(monkeypatch):
    class _FakeProc:
        returncode = 1
        stdout = ""
        stderr = "preflight failure"

    monkeypatch.setattr(cds.subprocess, "run", lambda *a, **k: _FakeProc())
    with pytest.raises(cds.CleanRoomAdapterError):
        cds.run_isolation_preflight()


def test_run_isolation_preflight_passes_on_zero_exit(monkeypatch):
    class _FakeProc:
        returncode = 0
        stdout = "ok"
        stderr = ""

    monkeypatch.setattr(cds.subprocess, "run", lambda *a, **k: _FakeProc())
    cds.run_isolation_preflight()  # must not raise


# ---------------------------------------------------------------------------
# compose_section -- preflight + broker invocation, no silent fallback
# ---------------------------------------------------------------------------


def test_compose_section_blocks_publication_on_broker_failure(monkeypatch, tmp_path):
    packet = _packet()
    section = {"id": "s1", "audience": "a new developer", "tone": "instructional", "depth": "brief"}

    monkeypatch.setattr(cds, "run_isolation_preflight", lambda: None)

    def _fake_run_inference(system_prompt, messages):
        return {"ok": False, "output": "", "usage": {}}

    with pytest.raises(cds.CleanRoomAdapterError):
        cds.compose_section(
            tmp_path, section, packet, schema_slug="demo", source_revision="abc123",
            run_inference=_fake_run_inference,
        )


def test_compose_section_blocks_publication_on_preflight_failure(monkeypatch, tmp_path):
    packet = _packet()
    section = {"id": "s1", "audience": "a new developer", "tone": "instructional", "depth": "brief"}

    def _fake_preflight():
        raise cds.CleanRoomAdapterError("preflight failed")

    called = {"run_inference": False}

    def _fake_run_inference(system_prompt, messages):
        called["run_inference"] = True
        return {"ok": True, "output": "should never be reached", "usage": {}}

    monkeypatch.setattr(cds, "run_isolation_preflight", _fake_preflight)
    with pytest.raises(cds.CleanRoomAdapterError):
        cds.compose_section(
            tmp_path, section, packet, schema_slug="demo", source_revision="abc123",
            run_inference=_fake_run_inference,
        )
    assert called["run_inference"] is False


def test_compose_section_returns_raw_output_on_success(monkeypatch, tmp_path):
    packet = _packet()
    section = {"id": "s1", "audience": "a new developer", "tone": "instructional", "depth": "brief"}

    monkeypatch.setattr(cds, "run_isolation_preflight", lambda: None)

    def _fake_run_inference(system_prompt, messages):
        assert "demo statement" in system_prompt
        return {"ok": True, "output": "Generated prose {{cite:CL-DEMO-001}}.", "usage": {}}

    result = cds.compose_section(
        tmp_path, section, packet, schema_slug="demo", source_revision="abc123",
        run_inference=_fake_run_inference,
    )
    assert "Generated prose" in result


def test_compose_section_rejects_tampered_packet_before_invoking_broker(monkeypatch, tmp_path):
    # Defends against alteration between write and use (§G.B point 2) --
    # even in the compose_section orchestration path, not just the
    # lower-level verify_packet_integrity unit test above.
    packet = _packet()
    monkeypatch.setattr(cds, "run_isolation_preflight", lambda: None)

    real_write = cds.write_section_packet

    def _tampering_write(*args, **kwargs):
        packet_path, manifest_path = real_write(*args, **kwargs)
        packet_path.write_text(
            packet_path.read_text(encoding="utf-8") + "tampered", encoding="utf-8",
        )
        return packet_path, manifest_path

    monkeypatch.setattr(cds, "write_section_packet", _tampering_write)

    called = {"run_inference": False}

    def _fake_run_inference(system_prompt, messages):
        called["run_inference"] = True
        return {"ok": True, "output": "never reached", "usage": {}}

    section = {"id": "s1", "audience": "a new developer", "tone": "instructional", "depth": "brief"}
    with pytest.raises(cds.CleanRoomAdapterError):
        cds.compose_section(
            tmp_path, section, packet, schema_slug="demo", source_revision="abc123",
            run_inference=_fake_run_inference,
        )
    assert called["run_inference"] is False


# ---------------------------------------------------------------------------
# parse_and_validate_response -- never trusts the model's own compliance claim
# ---------------------------------------------------------------------------


def test_parse_and_validate_response_rejects_citation_outside_packet():
    packet = _packet()
    text = "A fact {{cite:CL-NOT-IN-PACKET}}."
    body, findings = cds.parse_and_validate_response(text, packet)
    assert any(f.classification == "unsupported" for f in findings)


def test_parse_and_validate_response_accepts_valid_citation():
    packet = _packet()
    text = "A fact {{cite:CL-DEMO-001}}."
    body, findings = cds.parse_and_validate_response(text, packet)
    assert all(f.classification != "unsupported" for f in findings)
    assert "{{cite:" not in body  # citation tags stripped from the publishable body


def test_parse_and_validate_response_rejects_unexpected_file_marker():
    # The adapter must reject content that looks like it's trying to
    # declare a different output path/section than the one it was asked
    # to compose -- never trust the model's own claim about what it did.
    packet = _packet()
    text = "```file: docs/some-other-file.md\nsneaky content\n```"
    with pytest.raises(cds.CleanRoomAdapterError):
        cds.parse_and_validate_response(text, packet)
