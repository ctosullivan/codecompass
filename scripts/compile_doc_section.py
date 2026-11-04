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
import shutil
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
    project_root: Path,
    packet: dc.EvidencePacket,
    *,
    schema_slug: str,
    source_revision: str,
    staging_dir: Path | None = None,
) -> tuple[Path, Path]:
    """Writes the hydrated packet and its manifest to a fresh,
    ephemeral staging directory (`tempfile.mkdtemp`, or `staging_dir`
    if the caller already created one -- so `compose_section` can own
    that directory's whole lifecycle, including cleanup, hardening
    pass §N.C point 5) -- never under `project_root`, never a
    git-tracked path, never committed (§G.B point 1). The manifest
    records the pinned `source_revision` (the project's own `git
    rev-parse HEAD`, honestly recorded as dirty or clean by the caller),
    a `sha256` content hash of the exact written bytes (re-checked by
    `verify_packet_integrity` before every use, tamper detection), and
    `evidence_sha256` -- the canonical, reproducible hash of just the
    hydrated content (`doc_compiler.hash_evidence`), the same function
    used at publish time to detect whether the underlying knowledge has
    since changed (hardening pass §N.A/§N.C)."""
    staging_dir = staging_dir or Path(tempfile.mkdtemp(prefix="doc-compiler-section-packet-"))

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
        "evidence_sha256": dc.hash_evidence(packet.hydrated),
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

    The register/scope constraints below were tightened twice across
    three real Stage 87A demonstration runs against this same record
    (CL-CTXT-005) -- not a hypothetical, each round's independent
    semantic-support and editorial dispatch actually ran and actually
    found the problem named: round 1 found verification-style phrasing
    aimed at a reviewer ("you can confirm this is real...") and a
    self-referential aside about the project's own internal
    terminology drift (exactly the "resembles an audit report" failure
    mode the editorial bar exists to catch); round 2's broader
    "no tangent" instruction wasn't specific enough and the model
    reintroduced the same two problems in different wording (FAIL
    again, both reviewers); round 3's surgical fix -- naming the exact
    recurring phrasing to avoid and instructing the model to omit
    rather than rephrase a tangent the evidence itself mentions --
    produced a draft both independent reviewers passed. Kept this
    specific and literal rather than vaguer, since vaguer wording
    demonstrably did not work against this model and this evidence."""
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
        "something the reader should 'verify' or 'confirm' themselves, "
        "and never point to a specific file as proof that something is "
        "'real' rather than 'just a design' -- state the fact plainly "
        "instead and move on. Stay strictly on the section's own stated "
        "topic -- do not add any aside, in any wording, about a term "
        "being used in multiple/overlapping/related-but-distinct senses, "
        "about project terminology, or about project history, even if "
        "the evidence happens to mention it; if the evidence contains "
        "such an aside, simply omit it from your own output rather than "
        "rephrasing it. Stop writing as soon as the acceptance criteria "
        "are met -- a short, complete answer is correct; a longer one "
        "that adds anything beyond what was asked is not.\n\n"
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
) -> tuple[str, dict]:
    """Runs the isolation preflight, builds the ephemeral evidence
    handoff, re-verifies its integrity, then invokes the broker's own
    supported interface directly (no sandbox-boundary socket needed --
    see this module's own docstring for why). Raises
    `CleanRoomAdapterError` on any preflight, integrity, or broker
    failure; never a silent fallback to an un-isolated or un-validated
    attempt.

    Hardening pass §N.C correction: the broker's system prompt is now
    built from the packet **read back from the verified on-disk
    bytes**, not from the `packet` argument still held in memory --
    otherwise `verify_packet_integrity`'s own hash check proves nothing
    about what the broker actually receives, since the two could
    silently diverge (a mutation between write and use, or a future
    change that serializes them differently). The staging directory
    this function creates is always removed before returning, on both
    the success and every failure path (§N.C point 5) -- it is never
    left behind for a caller to clean up, and never committed.

    Returns `(output_text, manifest)` -- `manifest` is read back from
    the verified manifest file and carries the exact `schema_slug`,
    `section_id`, `source_revision`, `record_ids`, and hashes
    (`content_sha256`, `evidence_sha256`) of the evidence the broker
    was actually given, sufficient for a caller to bind a later review
    record to this exact compilation (§N.A)."""
    run_isolation_preflight()

    staging_dir = Path(tempfile.mkdtemp(prefix="doc-compiler-section-packet-"))
    try:
        packet_path, manifest_path = write_section_packet(
            project_root, packet, schema_slug=schema_slug, source_revision=source_revision,
            staging_dir=staging_dir,
        )
        assert_staging_dir_contents(staging_dir, packet_path, manifest_path)
        verify_packet_integrity(packet_path, manifest_path)

        verified_packet_raw = json.loads(packet_path.read_text(encoding="utf-8"))
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        verified_packet = dc.EvidencePacket(
            section_id=verified_packet_raw["section_id"],
            record_ids=verified_packet_raw["record_ids"],
            hydrated=verified_packet_raw["hydrated"],
            serialized_chars=len(packet_path.read_text(encoding="utf-8")),
        )

        system_prompt = build_system_prompt(schema_section, verified_packet)
        messages = [{"role": "user", "content": "Compose the section now."}]
        response = run_inference(system_prompt, messages)
        if not response.get("ok"):
            raise CleanRoomAdapterError(f"broker reported failure: {response}")
        output = response.get("output")
        if not isinstance(output, str) or not output:
            raise CleanRoomAdapterError("broker returned no usable output text")
        return output, manifest
    finally:
        shutil.rmtree(staging_dir, ignore_errors=True)


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
