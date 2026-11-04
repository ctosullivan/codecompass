"""Phase 87 Stage 87A clean-room section-compilation adapter
(restructuring-pass amendment finding B). See
planning/phase-87-documentation-schema-knowledge-compiled-documentation.md
§G.B for the full design this implements.

**Why this does not reuse `prepare_cleanroom_branch.py`'s export
mechanism, stated explicitly rather than left implicit.**
`prepare_cleanroom_branch.py`'s `_export_file_at_revision` runs `git
cat-file -p <revision>:<path>` -- it reads from git's object database
at a pinned revision, never from working-tree disk. A freshly
generated, uncommitted section-evidence packet has no git revision to
be exported "at," and this phase's own governing instruction is
explicit: never commit a transient evidence packet merely to export
it. This module therefore builds its own minimal, ephemeral,
hash-verified handoff instead of extending that script:

1. `write_section_packet` writes the hydrated packet plus a manifest
   (schema section id, pinned source revision, content sha256) to a
   fresh `tempfile.mkdtemp()` staging directory -- never a git-tracked
   path, never committed.
2. `verify_packet_integrity` re-checks the packet's on-disk content
   hash against the manifest's own recorded hash immediately before
   use -- a mismatch (altered between writing and use) is rejected,
   fail-closed.
3. `assert_staging_dir_contents` confirms the staging directory holds
   *exactly* the packet and its manifest, nothing else -- the
   narrative-documentation-exclusion discipline, enforced directly
   rather than by reusing `UnclassifiedNarrativeShapedFileError` (which
   is wired specifically to git-tracked broad exports).
4. `run_isolation_preflight` still runs the real, existing
   `verify_cleanroom_isolation.py` as a subprocess before every compile
   run and fails closed on non-zero exit -- a mechanism self-test,
   unchanged from the original design.
5. `compose_section` invokes `cleanroom_broker.run_inference` directly
   -- its own existing sanitised-env, neutral-cwd, no-tool subprocess
   call is the real isolation boundary for this bounded, self-contained
   text prompt. **No new namespace sandbox is constructed here**: this
   module's evidence is never a broad export for a classification gate
   to protect -- it is a small JSON blob built field-by-field
   exclusively from `knowledge_api.get()`'s own resolved content, with
   no file sweep in the first place. **No new clean-room broker is
   created.**

The adapter never trusts the model's own compliance claims:
`parse_and_validate_response` independently checks every returned
citation against the section's own resolved packet and rejects any
content declaring a different output path/section than the one
requested.

Mirrors `scripts/check_contracts.py`-style module conventions; not a
`codecompass` subcommand.
"""

from __future__ import annotations

import importlib.util
import json
import re
import subprocess
import sys
import tempfile
from collections.abc import Callable
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from codecompass import doc_compiler as dc  # noqa: E402
from codecompass import oracle as _oracle  # noqa: E402

_broker_spec = importlib.util.spec_from_file_location(
    "cleanroom_broker", ROOT / "scripts" / "cleanroom_broker.py"
)
cleanroom_broker = importlib.util.module_from_spec(_broker_spec)
_broker_spec.loader.exec_module(cleanroom_broker)

_VERIFY_ISOLATION_SCRIPT = ROOT / "scripts" / "verify_cleanroom_isolation.py"

_FILE_MARKER_RE = re.compile(r"```file:\s*(\S+)")


class CleanRoomAdapterError(Exception):
    """Raised for any condition that must block publication: a failed
    isolation preflight, a tampered or missing evidence packet, a
    broker failure, or returned content the adapter cannot
    independently confirm is within bounds. Never caught internally to
    publish a degraded result."""


def write_section_packet(
    project_root: Path, packet: dc.EvidencePacket, *, schema_slug: str, source_revision: str
) -> tuple[Path, Path]:
    """Writes the hydrated packet and its manifest to a fresh,
    ephemeral staging directory (`tempfile.mkdtemp`) -- never under
    `project_root`, never a git-tracked path, never committed (§G.B
    point 1). The manifest records the pinned `source_revision` (the
    project's own `git rev-parse HEAD`, honestly recorded as dirty or
    clean by the caller) and a `sha256` content hash, re-checked by
    `verify_packet_integrity` before every use."""
    staging_dir = Path(tempfile.mkdtemp(prefix="doc-compiler-section-packet-"))

    packet_path = staging_dir / f"{packet.section_id}.json"
    packet_content = json.dumps(
        {
            "section_id": packet.section_id,
            "record_ids": packet.record_ids,
            "hydrated": packet.hydrated,
        },
        sort_keys=True, indent=2,
    )
    packet_path.write_text(packet_content, encoding="utf-8")

    manifest_path = staging_dir / f"{packet.section_id}.manifest.json"
    manifest = {
        "schema_slug": schema_slug,
        "section_id": packet.section_id,
        "source_revision": source_revision,
        "record_ids": packet.record_ids,
        "content_sha256": _oracle.sha256_text(packet_content),
    }
    manifest_path.write_text(json.dumps(manifest, sort_keys=True, indent=2), encoding="utf-8")

    return packet_path, manifest_path


def verify_packet_integrity(packet_path: Path, manifest_path: Path) -> None:
    """Re-verifies the packet's current on-disk content hash against
    the manifest's own recorded hash immediately before use (§G.B
    point 2) -- a mismatch means the file was altered between writing
    and use, and is rejected, fail-closed, never used anyway."""
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    current_hash = _oracle.sha256_text(packet_path.read_text(encoding="utf-8"))
    if current_hash != manifest.get("content_sha256"):
        raise CleanRoomAdapterError(
            f"packet {packet_path} content hash {current_hash!r} does not match "
            f"its own manifest's recorded hash {manifest.get('content_sha256')!r} -- "
            "altered between writing and use; rejected, never used anyway"
        )


def assert_staging_dir_contents(staging_dir: Path, packet_path: Path, manifest_path: Path) -> None:
    """Confirms the staging directory holds *exactly* the packet and
    its manifest, nothing else (§G.B point 3) -- the narrative-
    documentation-exclusion discipline, enforced directly for this
    ephemeral directory rather than by reusing
    `UnclassifiedNarrativeShapedFileError` (wired to git-tracked broad
    exports specifically, not applicable here)."""
    expected = {packet_path.name, manifest_path.name}
    actual = {p.name for p in staging_dir.iterdir()}
    if actual != expected:
        unexpected = actual - expected
        raise CleanRoomAdapterError(
            f"staging directory {staging_dir} contains unexpected entries {sorted(unexpected)} -- "
            "expected exactly the packet and its manifest, nothing else"
        )


def run_isolation_preflight() -> None:
    """Runs the real, existing `verify_cleanroom_isolation.py` as a
    subprocess; raises `CleanRoomAdapterError` on any non-zero exit.
    Called once per compile run, not per section -- this is a mechanism
    self-test, not a per-call content check."""
    result = subprocess.run(
        [sys.executable, str(_VERIFY_ISOLATION_SCRIPT)],
        capture_output=True, text=True, timeout=180,
    )
    if result.returncode != 0:
        raise CleanRoomAdapterError(
            f"cleanroom isolation preflight failed (exit {result.returncode}): "
            f"{result.stdout}\n{result.stderr}"
        )


def build_system_prompt(schema_section: dict, packet: dc.EvidencePacket) -> str:
    """The section-specific writing contract (§C step 6): names the
    allowed output, the schema's own audience/tone/depth, and the
    mandatory per-sentence `{{cite:RECORD-ID}}` citation convention.

    The register/scope constraints below (write for the reader, not an
    auditor; stay on the stated topic; one clear point per sentence)
    were added after a real Stage 87A demonstration run's own
    independent editorial review found two genuine content problems:
    verification-style phrasing aimed at a reviewer ("you can confirm
    this is real...") rather than a newcomer, and an unrequested
    self-referential aside about the project's own internal
    terminology drift -- exactly the "resembles an audit report"
    failure mode this phase's own editorial bar exists to catch."""
    allowed_ids = ", ".join(packet.record_ids) if packet.record_ids else "(none)"
    return (
        "You are composing exactly one documentation section for an "
        "open-source project, from a fixed, bounded evidence packet. "
        f"Audience: {schema_section.get('audience', 'a developer new to the project')}. "
        f"Tone: {schema_section.get('tone', 'instructional')}. "
        f"Depth: {schema_section.get('depth', 'standard')}.\n\n"
        "Every sentence that states a fact must end with a citation tag "
        "in the exact form {{cite:RECORD-ID}}, naming one of the record "
        "ids listed below. Never cite any other id. Never invent a fact "
        "with no supporting record. Write only the section's own prose "
        "-- no headings claiming to be a different document, no file "
        "markers, no meta-commentary about this instruction.\n\n"
        "Write directly for the stated reader, not for someone auditing "
        "your output: state what is true as plain fact, never as "
        "something the reader should 'verify' or 'confirm' themselves. "
        "Stay strictly on the section's own stated topic -- do not add "
        "an aside about terminology inconsistency, project history, or "
        "any other tangent not directly needed to meet the acceptance "
        "criteria below, even if the evidence happens to mention it. "
        "Prefer one focused paragraph over several unless the depth "
        "setting above calls for more.\n\n"
        f"Permitted record ids for this section: {allowed_ids}.\n\n"
        f"Evidence (JSON): {json.dumps(packet.hydrated, sort_keys=True)}"
    )


def compose_section(
    project_root: Path,
    schema_section: dict,
    packet: dc.EvidencePacket,
    *,
    schema_slug: str,
    source_revision: str,
    run_inference: Callable[[str, list[dict]], dict] = cleanroom_broker.run_inference,
) -> str:
    """Runs the isolation preflight, builds the ephemeral evidence
    handoff, re-verifies its integrity, then invokes the broker's own
    supported interface directly (no sandbox-boundary socket needed --
    see this module's own docstring for why). Raises
    `CleanRoomAdapterError` on any preflight, integrity, or broker
    failure; never a silent fallback to an un-isolated or un-validated
    attempt."""
    run_isolation_preflight()

    packet_path, manifest_path = write_section_packet(
        project_root, packet, schema_slug=schema_slug, source_revision=source_revision,
    )
    assert_staging_dir_contents(packet_path.parent, packet_path, manifest_path)
    verify_packet_integrity(packet_path, manifest_path)

    system_prompt = build_system_prompt(schema_section, packet)
    messages = [{"role": "user", "content": "Compose the section now."}]
    response = run_inference(system_prompt, messages)
    if not response.get("ok"):
        raise CleanRoomAdapterError(f"broker reported failure: {response}")
    output = response.get("output")
    if not isinstance(output, str) or not output:
        raise CleanRoomAdapterError("broker returned no usable output text")
    return output


def parse_and_validate_response(
    raw_text: str, packet: dc.EvidencePacket
) -> tuple[str, list[dc.CitationFinding]]:
    """Never trusts the model's own compliance claims. Rejects content
    bearing a `file:` marker (an attempt to declare a different output
    path/section than the one requested). Validates every citation
    against the section's own resolved packet (scope check,
    `doc_compiler.validate_section_citations`) and strips citation tags
    from the returned publishable body."""
    marker = _FILE_MARKER_RE.search(raw_text)
    if marker is not None:
        raise CleanRoomAdapterError(
            f"returned content declares an unexpected file marker {marker.group(1)!r} -- "
            "rejected; the adapter never trusts the model's own claim about what it wrote"
        )
    findings = dc.validate_section_citations(raw_text, packet)
    body = dc.strip_citation_tags(raw_text).strip()
    return body, findings
