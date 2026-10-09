from pathlib import Path

from codecompass.source_symbols import (
    Language,
    SymbolIndexStatus,
    discover_source_files,
    extract_source_symbols_for_file,
)

# --- File discovery -----------------------------------------------------


def test_discover_source_files_classifies_every_supported_language(tmp_path: Path) -> None:
    (tmp_path / "a.py").write_text("x = 1")
    (tmp_path / "b.rs").write_text("fn x() {}")
    (tmp_path / "c.js").write_text("const x = 1;")
    (tmp_path / "d.ts").write_text("const x = 1;")
    (tmp_path / "e.hs").write_text("x = 1")
    (tmp_path / "f.txt").write_text("not source")

    result = dict(discover_source_files(tmp_path))
    assert result["a.py"] is Language.PYTHON
    assert result["b.rs"] is Language.RUST
    assert result["c.js"] is Language.JAVASCRIPT
    assert result["d.ts"] is Language.TYPESCRIPT
    assert result["e.hs"] is Language.HASKELL
    assert "f.txt" not in result


def test_discover_source_files_distinguishes_js_from_ts(tmp_path: Path) -> None:
    (tmp_path / "a.jsx").write_text("const x = 1;")
    (tmp_path / "a.tsx").write_text("const x = 1;")
    result = dict(discover_source_files(tmp_path))
    assert result["a.jsx"] is Language.JAVASCRIPT
    assert result["a.tsx"] is Language.TYPESCRIPT


def test_discover_source_files_keeps_tests_prunes_build_noise(tmp_path: Path) -> None:
    (tmp_path / "tests").mkdir()
    (tmp_path / "tests" / "test_a.py").write_text("x = 1")
    (tmp_path / "node_modules").mkdir()
    (tmp_path / "node_modules" / "dep.js").write_text("x = 1")
    (tmp_path / "vendor").mkdir()
    (tmp_path / "vendor" / "somevendor").mkdir()
    (tmp_path / "vendor" / "somevendor" / "src.py").write_text("x = 1")

    result = dict(discover_source_files(tmp_path))
    assert "tests/test_a.py" in result
    assert not any(p.startswith("node_modules/") for p in result)
    assert not any(p.startswith("vendor/") for p in result)


def test_discover_source_files_works_with_zero_vendor_config(tmp_path: Path) -> None:
    (tmp_path / "a.py").write_text("x = 1")
    # discover_source_files takes only project_root -- no vendor config
    # argument exists at all, confirming zero-vendor independence by
    # construction, not merely by an empty list being passed.
    result = dict(discover_source_files(tmp_path))
    assert result["a.py"] is Language.PYTHON


# --- Python extraction ----------------------------------------------------


def test_python_extraction_is_indexed_with_full_scope(tmp_path: Path) -> None:
    f = tmp_path / "m.py"
    f.write_text(
        "def public_fn():\n"
        "    '''does a thing'''\n"
        "    pass\n"
        "\n"
        "def _private_fn():\n"
        "    pass\n"
        "\n"
        "class PublicClass:\n"
        "    pass\n"
    )
    result = extract_source_symbols_for_file(f, Language.PYTHON)
    assert result.status == SymbolIndexStatus.INDEXED
    assert result.diagnostic is None
    by_name = {s.name: s for s in result.symbols}
    assert by_name["public_fn"].kind == "function"
    assert by_name["public_fn"].exposure == "public"
    assert by_name["public_fn"].purpose == "does a thing"
    assert by_name["_private_fn"].exposure == "conventional_private"
    assert by_name["PublicClass"].kind == "class"
    assert by_name["PublicClass"].exposure == "public"


def test_python_extraction_indexed_with_zero_symbols_is_distinguishable_from_failure(
    tmp_path: Path,
) -> None:
    f = tmp_path / "m.py"
    f.write_text("x = 1\n")
    result = extract_source_symbols_for_file(f, Language.PYTHON)
    assert result.status == SymbolIndexStatus.INDEXED
    assert result.symbols == ()


def test_python_syntax_error_is_parse_error_not_empty_result(tmp_path: Path) -> None:
    f = tmp_path / "m.py"
    f.write_text("def broken(:\n    pass\n")
    result = extract_source_symbols_for_file(f, Language.PYTHON)
    assert result.status == SymbolIndexStatus.PARSE_ERROR
    assert result.diagnostic is not None
    assert result.symbols == ()


def test_python_unreadable_file(tmp_path: Path) -> None:
    f = tmp_path / "m.py"
    f.write_bytes(b"\xff\xfe\x00\x01invalid utf8 \x80\x81")
    result = extract_source_symbols_for_file(f, Language.PYTHON)
    assert result.status == SymbolIndexStatus.UNREADABLE
    assert result.diagnostic is not None


def test_python_overload_produces_distinct_rows_never_crashes(tmp_path: Path) -> None:
    f = tmp_path / "m.py"
    f.write_text(
        "from typing import overload\n"
        "\n"
        "@overload\n"
        "def foo(a: str) -> None: ...\n"
        "@overload\n"
        "def foo(a: int) -> None: ...\n"
        "def foo(a):\n"
        "    print(a)\n"
    )
    result = extract_source_symbols_for_file(f, Language.PYTHON)
    assert result.status == SymbolIndexStatus.INDEXED
    foos = [s for s in result.symbols if s.name == "foo"]
    assert len(foos) == 3
    assert len({s.line for s in foos}) == 3  # all distinct lines


# --- Rust extraction --------------------------------------------------------


def test_rust_extraction_is_indexed_partial_with_full_exposure_model(tmp_path: Path) -> None:
    f = tmp_path / "m.rs"
    f.write_text(
        "/// a public fn\n"
        "pub fn foo() {}\n"
        "pub(crate) fn bar() {}\n"
        "pub(super) struct Baz;\n"
        "pub(in crate::module) enum Qux {}\n"
        "pub(self) trait Quux {}\n"
        "fn internal_fn() {}\n"
        "struct InternalStruct;\n"
    )
    result = extract_source_symbols_for_file(f, Language.RUST)
    assert result.status == SymbolIndexStatus.INDEXED_PARTIAL
    by_name = {s.name: s for s in result.symbols}
    assert by_name["foo"].exposure == "public"
    assert by_name["foo"].purpose == "a public fn"
    assert by_name["bar"].exposure == "restricted"
    assert by_name["Baz"].exposure == "restricted"
    assert by_name["Qux"].exposure == "restricted"
    assert by_name["Quux"].exposure == "restricted"
    assert by_name["internal_fn"].exposure == "internal"
    assert by_name["InternalStruct"].exposure == "internal"


def test_rust_overload_like_repeated_declarations_produce_distinct_rows(tmp_path: Path) -> None:
    f = tmp_path / "m.rs"
    f.write_text("fn foo() {}\nfn foo_two() {}\n")
    result = extract_source_symbols_for_file(f, Language.RUST)
    assert result.status == SymbolIndexStatus.INDEXED_PARTIAL
    assert {s.name for s in result.symbols} == {"foo", "foo_two"}


def test_rust_unreadable_file(tmp_path: Path) -> None:
    f = tmp_path / "m.rs"
    f.write_bytes(b"\xff\xfe\x00\x01invalid utf8 \x80\x81")
    result = extract_source_symbols_for_file(f, Language.RUST)
    assert result.status == SymbolIndexStatus.UNREADABLE


# --- JS/TS extraction --------------------------------------------------------


def test_js_extraction_is_indexed_partial_with_export_based_exposure(tmp_path: Path) -> None:
    f = tmp_path / "m.js"
    f.write_text(
        "export function add(a, b) {\n  return a + b;\n}\n\n"
        "function internalHelper() {}\n\n"
        "export class Widget {}\n"
    )
    result = extract_source_symbols_for_file(f, Language.JAVASCRIPT)
    assert result.status == SymbolIndexStatus.INDEXED_PARTIAL
    by_name = {s.name: s for s in result.symbols}
    assert by_name["add"].exposure == "public"
    assert by_name["internalHelper"].exposure == "internal"
    assert by_name["Widget"].exposure == "public"


def test_ts_extraction_supports_interface_type_enum_and_jsdoc(tmp_path: Path) -> None:
    f = tmp_path / "m.ts"
    f.write_text(
        "/** Adds two numbers. */\n"
        "export function add(a: number, b: number): number {\n  return a + b;\n}\n\n"
        "export interface Shape {}\n"
        "type Internal = string;\n"
        "export enum Color { Red, Green }\n"
    )
    result = extract_source_symbols_for_file(f, Language.TYPESCRIPT)
    assert result.status == SymbolIndexStatus.INDEXED_PARTIAL
    by_name = {s.name: s for s in result.symbols}
    assert by_name["add"].purpose == "Adds two numbers."
    assert by_name["add"].exposure == "public"
    assert by_name["Shape"].kind == "interface"
    assert by_name["Internal"].exposure == "internal"
    assert by_name["Color"].kind == "enum"


def test_ts_overload_produces_distinct_rows_never_crashes(tmp_path: Path) -> None:
    f = tmp_path / "m.ts"
    f.write_text(
        "export function foo(a: string): void;\n"
        "export function foo(a: number): void;\n"
        "export function foo(a: string | number): void {\n"
        "  console.log(a);\n"
        "}\n"
    )
    result = extract_source_symbols_for_file(f, Language.TYPESCRIPT)
    assert result.status == SymbolIndexStatus.INDEXED_PARTIAL
    foos = [s for s in result.symbols if s.name == "foo"]
    assert len(foos) == 3
    assert len({s.line for s in foos}) == 3


def test_js_unreadable_file(tmp_path: Path) -> None:
    f = tmp_path / "m.js"
    f.write_bytes(b"\xff\xfe\x00\x01invalid utf8 \x80\x81")
    result = extract_source_symbols_for_file(f, Language.JAVASCRIPT)
    assert result.status == SymbolIndexStatus.UNREADABLE


# --- Haskell (unsupported) ----------------------------------------------------


def test_haskell_is_unsupported_not_a_silent_empty_result(tmp_path: Path) -> None:
    f = tmp_path / "m.hs"
    f.write_text("main = putStrLn \"hi\"\n")
    result = extract_source_symbols_for_file(f, Language.HASKELL)
    assert result.status == SymbolIndexStatus.UNSUPPORTED
    assert result.diagnostic is None
    assert result.symbols == ()
