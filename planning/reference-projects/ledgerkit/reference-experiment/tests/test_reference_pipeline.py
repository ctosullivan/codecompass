"""Tests for the Phase 54 reference-ingestion pipeline.

Runs against the real, already-pinned local hledger clone
(`/home/cormac/projects/hledger`) — a local git repository, not a live
network call (`decisions/0014`'s "no test makes a real external call"
posture, honoured here even though this module lives outside
`src/codecompass/`). Skipped entirely if that clone isn't present, so
the suite stays runnable in an environment without it.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

import reference_pipeline as rp  # noqa: E402

_HLEDGER_CLONE = Path("/home/cormac/projects/hledger")
_REFERENCES_TOML = Path(__file__).parent.parent / "references.toml"

pytestmark = pytest.mark.skipif(
    not _HLEDGER_CLONE.is_dir(), reason="local hledger clone not present in this environment"
)

_EXPECTED_COMMIT = "33fa849e7ae841968bd21c427094c4fb4a4ec38d"


def test_load_references_toml_parses_the_real_file() -> None:
    sources = rp.load_references_toml(_REFERENCES_TOML)
    assert len(sources) == 1
    hledger = sources[0]
    assert hledger.name == "hledger"
    assert hledger.requested_ref == "1.52.4"
    assert hledger.local_path == str(_HLEDGER_CLONE)
    assert len(hledger.selections) == 8
    labels = {sel.label for sel in hledger.selections}
    assert "tag-query-manual" in labels
    assert "tag-query-parser" in labels


def test_resolve_ref_matches_the_already_known_pinned_commit() -> None:
    sources = rp.load_references_toml(_REFERENCES_TOML)
    resolved_commit = rp.resolve_ref(sources[0])
    assert resolved_commit == _EXPECTED_COMMIT


def test_resolve_ref_raises_for_an_unknown_tag() -> None:
    bad = rp.ReferenceSource(
        name="hledger",
        source="git",
        url="https://github.com/simonmichael/hledger",
        requested_ref="99.99.99-does-not-exist",
        local_path=str(_HLEDGER_CLONE),
        selections=(),
    )
    with pytest.raises(rp.ReferencePipelineError, match="not found"):
        rp.resolve_ref(bad)


def test_extract_lines_matches_real_source_content() -> None:
    sources = rp.load_references_toml(_REFERENCES_TOML)
    resolved, texts = rp.resolve_and_extract(sources[0])
    assert resolved.resolved_commit == _EXPECTED_COMMIT
    assert resolved.fetch_method == "local_clone"

    parser_text = texts["tag-query-parser"]
    assert "parseTag" in parser_text
    assert "T.break" in parser_text

    manual_text = texts["tag-query-manual"]
    assert "tag: query" in manual_text
    assert "NAMEREGEX" in manual_text


def test_content_hash_is_deterministic_across_runs() -> None:
    sources = rp.load_references_toml(_REFERENCES_TOML)
    resolved_1, _ = rp.resolve_and_extract(sources[0])
    resolved_2, _ = rp.resolve_and_extract(sources[0])

    hashes_1 = {sel.label: sel.content_hash for sel in resolved_1.selections}
    hashes_2 = {sel.label: sel.content_hash for sel in resolved_2.selections}
    assert hashes_1 == hashes_2
    assert all(len(h) == 64 for h in hashes_1.values())  # sha256 hex digest length


def test_extract_lines_out_of_range_raises() -> None:
    bad_selection = rp.ReferenceSelection(
        label="bad", path="hledger-lib/Hledger/Query.hs", start_line=1, end_line=10_000_000, note=""
    )
    with pytest.raises(rp.ReferencePipelineError, match="out of range"):
        rp._extract_lines(_HLEDGER_CLONE, bad_selection)


def test_tag_query_manual_excerpt_contains_all_three_inheritance_rules() -> None:
    """Regression test for a real defect this experiment's own evaluation
    caught (`54-tag-query-semantics-reference-experiment-evaluation.md`,
    FAIL verdict): the original `tag-query-manual` selection's line range
    silently excluded the third tag-inheritance rule while its own
    description claimed all three were present. Content-hash pinning
    guarantees an excerpt hasn't silently changed; it does not guarantee
    the excerpt's boundary actually covers what its description claims —
    this test is that second guarantee, made explicit and checked.
    """
    sources = rp.load_references_toml(_REFERENCES_TOML)
    _resolved, texts = rp.resolve_and_extract(sources[0])
    manual_text = texts["tag-query-manual"]
    assert "Accounts also inherit the tags of their parent accounts" in manual_text
    assert "Postings also inherit the tags of their account" in manual_text
    assert "Transactions also acquire the tags of their postings" in manual_text


def test_extract_lines_missing_file_raises() -> None:
    bad_selection = rp.ReferenceSelection(
        label="bad", path="does/not/exist.hs", start_line=1, end_line=2, note=""
    )
    with pytest.raises(rp.ReferencePipelineError, match="not found"):
        rp._extract_lines(_HLEDGER_CLONE, bad_selection)


def test_write_lock_and_extracted_markdown_round_trip(tmp_path: Path) -> None:
    sources = rp.load_references_toml(_REFERENCES_TOML)
    resolved_all = rp.run_pipeline(
        _REFERENCES_TOML, tmp_path / "extracted", tmp_path / "references.lock"
    )
    assert len(resolved_all) == 1

    lock_content = (tmp_path / "references.lock").read_text(encoding="utf-8")
    assert _EXPECTED_COMMIT in lock_content
    assert "tag-query-parser" in lock_content
    assert "sha256:" in lock_content

    extracted_files = sorted((tmp_path / "extracted").glob("*.md"))
    assert len(extracted_files) == len(sources[0].selections)
    for file_path in extracted_files:
        content = file_path.read_text(encoding="utf-8")
        assert content.startswith("---\n")
        assert f"resolved_commit: {_EXPECTED_COMMIT}" in content
        assert "content_hash: sha256:" in content


def test_pipeline_is_idempotent_up_to_timestamps(tmp_path: Path) -> None:
    rp.run_pipeline(_REFERENCES_TOML, tmp_path / "run1", tmp_path / "run1.lock")
    rp.run_pipeline(_REFERENCES_TOML, tmp_path / "run2", tmp_path / "run2.lock")

    run1_files = {p.name: p.read_text(encoding="utf-8") for p in (tmp_path / "run1").glob("*.md")}
    run2_files = {p.name: p.read_text(encoding="utf-8") for p in (tmp_path / "run2").glob("*.md")}
    assert set(run1_files) == set(run2_files)
    for name in run1_files:
        # Every line except the frontmatter's extracted_at timestamp is
        # byte-identical between runs.
        def _without_timestamp(text: str) -> list[str]:
            return [line for line in text.splitlines() if not line.startswith("extracted_at:")]

        assert _without_timestamp(run1_files[name]) == _without_timestamp(run2_files[name])


_LK_COMPAT_QUERY_DATE_001 = Path(
    "/home/cormac/projects/ledgerkit/dev-docs/compat-register/LK-COMPAT-QUERY-DATE-001.yaml"
)

pytestmark_ledgerkit = pytest.mark.skipif(
    not _LK_COMPAT_QUERY_DATE_001.is_file(),
    reason="real Ledgerkit clone with compat-register entries not present",
)


@pytestmark_ledgerkit
def test_parse_compat_register_source_evidence_reads_real_citations() -> None:
    yaml_text = _LK_COMPAT_QUERY_DATE_001.read_text(encoding="utf-8")
    citations = rp.parse_compat_register_source_evidence(yaml_text)
    assert citations, "expected at least one kind: source citation"
    paths = {path for path, _ in citations}
    assert any(path.endswith("Dates.hs") for path in paths)
    all_line_numbers = {n for _, nums in citations for n in nums}
    assert 429 in all_line_numbers
    assert 1132 in all_line_numbers
    assert 1148 in all_line_numbers


@pytestmark_ledgerkit
def test_match_compat_register_evidence_finds_real_overlap() -> None:
    """The §3.3 fallback, demonstrated against a real, already-published
    compat-register entry (no `tag:` entry exists yet — that's the gap
    this phase's chosen task fills — so this proves the *mechanism*
    against the nearest real equivalent, the `date:` family's own
    entry, which cites the exact two line ranges this experiment also
    extracted).
    """
    sources = rp.load_references_toml(_REFERENCES_TOML)
    resolved, _texts = rp.resolve_and_extract(sources[0])
    yaml_text = _LK_COMPAT_QUERY_DATE_001.read_text(encoding="utf-8")

    matched = rp.match_compat_register_evidence(resolved, yaml_text)
    matched_labels = {sel.label for sel in matched}
    assert matched_labels == {"date-query-span-single", "date-query-span-double"}

    # And, as a negative control: mechanical mentions_artifact detection
    # (CodeCompass's own existing, unmodified mechanism) found zero edges
    # for this exact pairing when run for real against a scratch
    # Ledgerkit copy this phase (see the phase retro/evaluation report) —
    # this fallback exists precisely because that path came back empty.


def test_local_clone_at_a_different_commit_is_rejected(tmp_path: Path) -> None:
    """A stale/moved-on local clone must never be silently treated as
    pinned — the mechanical guarantee behind `references.lock`'s
    provenance claim.
    """
    mismatched = rp.ReferenceSource(
        name="hledger",
        source="git",
        url="https://github.com/simonmichael/hledger",
        requested_ref="1.52.4",
        local_path=str(_HLEDGER_CLONE),
        selections=(),
    )
    # Resolve against 1.52.4, but pretend the clone is actually at a
    # different (also-real) commit to force the mismatch path.
    real_commit = rp.resolve_ref(mismatched)
    fake_commit = "0" * 40
    assert real_commit != fake_commit
    with pytest.raises(rp.ReferencePipelineError, match="not the resolved commit"):
        rp._read_source_root(mismatched, fake_commit)
