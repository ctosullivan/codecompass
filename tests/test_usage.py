from pathlib import Path

from codecompass.core import Ecosystem, VendorConfig
from codecompass.usage import (
    DetectedImport,
    detect_imports_for_file,
    detect_npm_imports,
    detect_python_imports,
    detect_rust_imports,
    resolve_project_usage,
)


def _config(name: str, ecosystem: Ecosystem) -> VendorConfig:
    return VendorConfig(name=name, ecosystem=ecosystem)


# --- detect_python_imports ---------------------------------------------------


def test_detect_python_imports_module_level_import_is_vendor_level(tmp_path: Path) -> None:
    path = tmp_path / "mod.py"
    path.write_text("import rich\n", encoding="utf-8")

    assert detect_python_imports(path) == [
        DetectedImport(vendor="rich", symbol_name=None, line=1)
    ]


def test_detect_python_imports_dotted_import_uses_top_level_component(tmp_path: Path) -> None:
    path = tmp_path / "mod.py"
    path.write_text("import rich.console\n", encoding="utf-8")

    assert detect_python_imports(path) == [
        DetectedImport(vendor="rich", symbol_name=None, line=1)
    ]


def test_detect_python_imports_from_import_captures_one_entry_per_bound_name(
    tmp_path: Path,
) -> None:
    path = tmp_path / "mod.py"
    path.write_text("from rich.console import Console, Text\n", encoding="utf-8")

    assert detect_python_imports(path) == [
        DetectedImport(vendor="rich", symbol_name="Console", line=1),
        DetectedImport(vendor="rich", symbol_name="Text", line=1),
    ]


def test_detect_python_imports_nested_inside_function_still_counts(tmp_path: Path) -> None:
    path = tmp_path / "mod.py"
    path.write_text("def lazy():\n    import rich\n", encoding="utf-8")

    assert detect_python_imports(path) == [
        DetectedImport(vendor="rich", symbol_name=None, line=2)
    ]


def test_detect_python_imports_relative_imports_are_ignored(tmp_path: Path) -> None:
    path = tmp_path / "mod.py"
    path.write_text("from . import sibling\nfrom .sibling import thing\n", encoding="utf-8")

    assert detect_python_imports(path) == []


def test_detect_python_imports_unparseable_file_returns_empty(tmp_path: Path) -> None:
    path = tmp_path / "broken.py"
    path.write_text("def broken(:\n", encoding="utf-8")

    assert detect_python_imports(path) == []


def test_detect_python_imports_attribute_access_upgrades_to_symbol_level(
    tmp_path: Path,
) -> None:
    path = tmp_path / "mod.py"
    path.write_text("import rich\nrich.Console()\n", encoding="utf-8")

    assert detect_python_imports(path) == [
        DetectedImport(vendor="rich", symbol_name=None, line=1),
        DetectedImport(vendor="rich", symbol_name="Console", line=2),
    ]


def test_detect_python_imports_attribute_access_resolves_via_alias(tmp_path: Path) -> None:
    path = tmp_path / "mod.py"
    path.write_text("import rich as r\nr.Console()\n", encoding="utf-8")

    assert detect_python_imports(path) == [
        DetectedImport(vendor="rich", symbol_name=None, line=1),
        DetectedImport(vendor="rich", symbol_name="Console", line=2),
    ]


def test_detect_python_imports_deep_attribute_chain_resolves_only_first_attribute(
    tmp_path: Path,
) -> None:
    path = tmp_path / "mod.py"
    path.write_text("import rich\nrich.console.Console()\n", encoding="utf-8")

    assert detect_python_imports(path) == [
        DetectedImport(vendor="rich", symbol_name=None, line=1),
        DetectedImport(vendor="rich", symbol_name="console", line=2),
    ]


def test_detect_python_imports_no_attribute_access_keeps_vendor_level_only(
    tmp_path: Path,
) -> None:
    path = tmp_path / "mod.py"
    path.write_text("import rich\n\ndef use():\n    return rich\n", encoding="utf-8")

    assert detect_python_imports(path) == [
        DetectedImport(vendor="rich", symbol_name=None, line=1)
    ]


# --- detect_npm_imports -------------------------------------------------------


def test_detect_npm_imports_named_import_one_entry_per_name(tmp_path: Path) -> None:
    path = tmp_path / "app.ts"
    path.write_text('import { Console, Text } from "rich";\n', encoding="utf-8")

    assert detect_npm_imports(path) == [
        DetectedImport(vendor="rich", symbol_name="Console", line=1),
        DetectedImport(vendor="rich", symbol_name="Text", line=1),
    ]


def test_detect_npm_imports_named_import_strips_local_alias(tmp_path: Path) -> None:
    path = tmp_path / "app.ts"
    path.write_text('import { Console as C } from "rich";\n', encoding="utf-8")

    assert detect_npm_imports(path) == [
        DetectedImport(vendor="rich", symbol_name="Console", line=1)
    ]


def test_detect_npm_imports_default_import_is_vendor_level(tmp_path: Path) -> None:
    path = tmp_path / "app.ts"
    path.write_text('import Foo from "foo-pkg";\n', encoding="utf-8")

    assert detect_npm_imports(path) == [
        DetectedImport(vendor="foo-pkg", symbol_name=None, line=1)
    ]


def test_detect_npm_imports_namespace_import_is_vendor_level(tmp_path: Path) -> None:
    path = tmp_path / "app.ts"
    path.write_text('import * as foo from "foo-pkg";\n', encoding="utf-8")

    assert detect_npm_imports(path) == [
        DetectedImport(vendor="foo-pkg", symbol_name=None, line=1)
    ]


def test_detect_npm_imports_require_is_vendor_level(tmp_path: Path) -> None:
    path = tmp_path / "app.js"
    path.write_text('const foo = require("foo-pkg");\n', encoding="utf-8")

    assert detect_npm_imports(path) == [
        DetectedImport(vendor="foo-pkg", symbol_name=None, line=1)
    ]


def test_detect_npm_imports_unreadable_file_returns_empty(tmp_path: Path) -> None:
    path = tmp_path / "missing.ts"

    assert detect_npm_imports(path) == []


# --- detect_rust_imports -------------------------------------------------------


def test_detect_rust_imports_symbol_use(tmp_path: Path) -> None:
    path = tmp_path / "main.rs"
    path.write_text("use serde::Deserialize;\n", encoding="utf-8")

    assert detect_rust_imports(path) == [
        DetectedImport(vendor="serde", symbol_name="Deserialize", line=1)
    ]


def test_detect_rust_imports_multi_segment_path_uses_first_and_last_component(
    tmp_path: Path,
) -> None:
    path = tmp_path / "main.rs"
    path.write_text("use tokio::sync::Mutex;\n", encoding="utf-8")

    assert detect_rust_imports(path) == [
        DetectedImport(vendor="tokio", symbol_name="Mutex", line=1)
    ]


def test_detect_rust_imports_wildcard_is_vendor_level(tmp_path: Path) -> None:
    path = tmp_path / "main.rs"
    path.write_text("use serde::*;\n", encoding="utf-8")

    assert detect_rust_imports(path) == [
        DetectedImport(vendor="serde", symbol_name=None, line=1)
    ]


def test_detect_rust_imports_bare_crate_is_vendor_level(tmp_path: Path) -> None:
    path = tmp_path / "main.rs"
    path.write_text("use serde;\n", encoding="utf-8")

    assert detect_rust_imports(path) == [
        DetectedImport(vendor="serde", symbol_name=None, line=1)
    ]


# --- detect_imports_for_file dispatcher ---------------------------------------


def test_detect_imports_for_file_dispatches_by_ecosystem_and_suffix(tmp_path: Path) -> None:
    py_path = tmp_path / "mod.py"
    py_path.write_text("import rich\n", encoding="utf-8")

    assert detect_imports_for_file(py_path, Ecosystem.PYTHON) == [
        DetectedImport(vendor="rich", symbol_name=None, line=1)
    ]
    assert detect_imports_for_file(py_path, Ecosystem.CARGO) == []
    assert detect_imports_for_file(py_path, Ecosystem.NPM) == []


def test_detect_imports_for_file_unclaimed_suffix_returns_empty(tmp_path: Path) -> None:
    path = tmp_path / "README.md"
    path.write_text("# hello\n", encoding="utf-8")

    assert detect_imports_for_file(path, Ecosystem.PYTHON) == []


# --- resolve_project_usage -----------------------------------------------------


def test_resolve_project_usage_filters_out_untracked_packages(tmp_path: Path) -> None:
    (tmp_path / "app.py").write_text("import rich\nimport untracked_pkg\n", encoding="utf-8")
    configs = [_config("rich", Ecosystem.PYTHON)]

    results = resolve_project_usage(tmp_path, configs)

    assert results == [("app.py", DetectedImport(vendor="rich", symbol_name=None, line=1))]


def test_resolve_project_usage_scans_project_test_directories(tmp_path: Path) -> None:
    """Unlike `filetree`'s vendor-source walk, project scanning must NOT
    exclude tests/fixtures — a project's own test files importing a
    vendor is real usage signal.
    """
    tests_dir = tmp_path / "tests"
    tests_dir.mkdir()
    (tests_dir / "test_app.py").write_text("import rich\n", encoding="utf-8")
    configs = [_config("rich", Ecosystem.PYTHON)]

    results = resolve_project_usage(tmp_path, configs)

    assert results == [
        ("tests/test_app.py", DetectedImport(vendor="rich", symbol_name=None, line=1))
    ]


def test_resolve_project_usage_excludes_node_modules_and_venv_noise(tmp_path: Path) -> None:
    (tmp_path / "node_modules").mkdir()
    (tmp_path / "node_modules" / "noise.js").write_text(
        'import Foo from "foo-pkg";\n', encoding="utf-8"
    )
    configs = [_config("foo-pkg", Ecosystem.NPM)]

    assert resolve_project_usage(tmp_path, configs) == []


def test_resolve_project_usage_excludes_codecompass_vendor_output_dir(tmp_path: Path) -> None:
    """`vendor/<name>/src/` is a cloned upstream snapshot (Phase 13,
    `decisions/0033`), not the consuming project's own source — a
    self-import inside a vendor's own cloned code (e.g. its own package
    name appearing in its own source) must not register as this project
    using that vendor, or usage-driven enrichment selection
    (`decisions/0031`) would treat nearly every tracked vendor as "used"
    regardless of whether the project's own code imports it.
    """
    vendor_src = tmp_path / "vendor" / "rich" / "src"
    vendor_src.mkdir(parents=True)
    (vendor_src / "__init__.py").write_text("import rich\n", encoding="utf-8")
    configs = [_config("rich", Ecosystem.PYTHON)]

    assert resolve_project_usage(tmp_path, configs) == []


def test_resolve_project_usage_across_mixed_ecosystem_project(tmp_path: Path) -> None:
    (tmp_path / "app.py").write_text("from rich.console import Console\n", encoding="utf-8")
    (tmp_path / "app.ts").write_text('import { Table } from "cli-table";\n', encoding="utf-8")
    (tmp_path / "main.rs").write_text("use serde::Deserialize;\n", encoding="utf-8")
    configs = [
        _config("rich", Ecosystem.PYTHON),
        _config("cli-table", Ecosystem.NPM),
        _config("serde", Ecosystem.CARGO),
    ]

    results = resolve_project_usage(tmp_path, configs)

    assert set(results) == {
        ("app.py", DetectedImport(vendor="rich", symbol_name="Console", line=1)),
        ("app.ts", DetectedImport(vendor="cli-table", symbol_name="Table", line=1)),
        ("main.rs", DetectedImport(vendor="serde", symbol_name="Deserialize", line=1)),
    }
