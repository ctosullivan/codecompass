"""Validates `codecompass-adaptor-protocol`'s own conformance manifest
from this repository's side — the Python-side half of "any
implementation, in any language, validates against these vectors"
(`conformance/README.md` in that repository). Skips cleanly if the
submodule isn't checked out, matching `decisions/0014`'s posture.
"""

from pathlib import Path

import pytest

jsonschema = pytest.importorskip("jsonschema")

_PROTOCOL_ROOT = (
    Path(__file__).resolve().parents[1] / "protocol" / "codecompass-adaptor-protocol"
)
_MANIFEST = _PROTOCOL_ROOT / "conformance" / "manifest.json"


@pytest.mark.skipif(
    not _MANIFEST.is_file(),
    reason="protocol/codecompass-adaptor-protocol/ git submodule not initialized",
)
def test_conformance_manifest_vectors_match_expected_validity() -> None:
    import json

    manifest = json.loads(_MANIFEST.read_text())
    failures = []
    for entry in manifest["vectors"]:
        schema = json.loads((_PROTOCOL_ROOT / entry["schema"]).read_text())
        instance = json.loads((_PROTOCOL_ROOT / entry["vector"]).read_text())
        errors = list(jsonschema.Draft202012Validator(schema).iter_errors(instance))
        is_valid = not errors
        expected_valid = entry["expect"] == "valid"
        if is_valid != expected_valid:
            failures.append((entry, [str(e) for e in errors]))
    assert not failures, failures


@pytest.mark.skipif(
    not _MANIFEST.is_file(),
    reason="protocol/codecompass-adaptor-protocol/ git submodule not initialized",
)
def test_real_analyze_project_response_shape_used_by_haskell_adapter_validates() -> None:
    """`HaskellAdapter`'s own parsing (`entry["name"]`, `entry.get("purpose")`,
    `entry["module"]`, `entry.get("kind")`, `entry.get("note")`) must
    agree with what the protocol repository's own schema actually
    allows — this is the cross-check that would have caught the gap
    `decisions/0059` fixed, had it existed beforehand.
    """
    import json

    from jsonschema import Draft202012Validator

    schema = json.loads(
        (_PROTOCOL_ROOT / "schemas" / "analyze_project-response.json").read_text()
    )
    instance = {
        "id": 2,
        "result": {
            "symbols": [
                {"name": "doThing", "purpose": "does the thing", "module": "Demo.Core"},
                {
                    "name": "X",
                    "purpose": None,
                    "module": "Demo.Core",
                    "kind": "reexport",
                    "note": "alias for Demo.Internal.A",
                },
                {
                    "name": "Year",
                    "purpose": None,
                    "module": "Demo.Types",
                    "kind": "undetermined",
                    "note": "gated by a CPP conditional",
                },
            ]
        },
    }
    Draft202012Validator(schema).validate(instance)
