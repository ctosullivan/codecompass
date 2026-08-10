from pathlib import Path

from depcompass.core import Ecosystem
from depcompass.symbols import (
    Symbol,
    extract_npm_symbols,
    extract_python_symbols,
    extract_rust_symbols,
    extract_symbols_for_file,
    purpose_for_file,
)

FIXTURES = Path(__file__).parent / "fixtures"


def test_extract_rust_symbols_captures_names_and_docs() -> None:
    symbols = extract_rust_symbols(FIXTURES / "sample_lib.rs")
    by_name = {s.name: s for s in symbols}

    assert by_name["add"].purpose == "Adds two numbers together."
    assert "Point" in by_name
    assert by_name["Point"].purpose is None
    assert "internal_helper" not in by_name  # not pub


def test_extract_rust_symbols_name_capture_unaffected_by_multiline_signature() -> None:
    """Unlike the old string-signature-based extraction, name-only
    extraction isn't truncated by a multi-line signature — the function
    name is fully present on the opening `pub fn` line regardless."""
    symbols = extract_rust_symbols(FIXTURES / "sample_lib.rs")
    by_name = {s.name: s for s in symbols}

    assert "multi_line_signature" in by_name


def test_extract_rust_symbols_missing_file_returns_empty(tmp_path: Path) -> None:
    assert extract_rust_symbols(tmp_path / "nope.rs") == []


def test_extract_python_symbols_captures_names_and_docstrings() -> None:
    symbols = extract_python_symbols(FIXTURES / "sample_module_with_all.py")
    by_name = {s.name: s for s in symbols}

    assert by_name["greet"].purpose == "Return a friendly greeting."
    assert by_name["Greeter"].purpose == "Greets people repeatedly."


def test_extract_python_symbols_missing_file_returns_empty(tmp_path: Path) -> None:
    assert extract_python_symbols(tmp_path / "nope.py") == []


def test_extract_python_symbols_syntax_error_returns_empty(tmp_path: Path) -> None:
    bad = tmp_path / "bad.py"
    bad.write_text("def broken(:\n", encoding="utf-8")
    assert extract_python_symbols(bad) == []


def test_extract_npm_symbols_without_jsdoc() -> None:
    symbols = extract_npm_symbols(FIXTURES / "sample.d.ts")
    by_name = {s.name: s for s in symbols}

    assert set(by_name) == {"Options", "TurndownService"}
    assert by_name["TurndownService"].purpose is None


def test_extract_npm_symbols_with_jsdoc() -> None:
    symbols = extract_npm_symbols(FIXTURES / "sample_with_jsdoc.d.ts")

    assert symbols == [Symbol(name="convert", purpose="Converts HTML to Markdown.")]


def test_extract_symbols_for_file_gates_on_ecosystem_and_suffix() -> None:
    # A Python file handed to the npm/cargo extractors' dispatch should
    # not be parsed as TypeScript or Rust.
    assert extract_symbols_for_file(FIXTURES / "sample_module_with_all.py", Ecosystem.NPM) == []
    assert extract_symbols_for_file(FIXTURES / "sample_module_with_all.py", Ecosystem.CARGO) == []
    assert extract_symbols_for_file(FIXTURES / "sample_lib.rs", Ecosystem.CARGO) != []


def test_purpose_for_file_prefers_ecosystem_symbol_purpose() -> None:
    assert purpose_for_file(FIXTURES / "sample_lib.rs", Ecosystem.CARGO) == (
        "Adds two numbers together."
    )
    assert purpose_for_file(FIXTURES / "sample_module_with_all.py", Ecosystem.PYTHON) == (
        "Return a friendly greeting."
    )


def test_purpose_for_file_falls_back_to_generic_hash_comment() -> None:
    purpose = purpose_for_file(FIXTURES / "generic_hash_comment.cfg", Ecosystem.PYTHON)
    assert purpose == "Runtime configuration defaults for the demo service."


def test_purpose_for_file_falls_back_to_generic_slash_comment() -> None:
    purpose = purpose_for_file(FIXTURES / "generic_slash_comment.js", Ecosystem.NPM)
    assert purpose == "CLI entry point."


def test_purpose_for_file_returns_none_for_non_comment_leading_line(tmp_path: Path) -> None:
    data_file = tmp_path / "data.json"
    data_file.write_text('{\n  "a": 1\n}\n', encoding="utf-8")
    assert purpose_for_file(data_file, Ecosystem.NPM) is None
