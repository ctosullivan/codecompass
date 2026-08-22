from pathlib import Path

from codecompass.claude_md import (
    read_enrichment_hash,
    read_installed_version,
    render_vendor_claude_md,
    update_description_section,
)
from codecompass.core import Depth, Ecosystem, VendorConfig, VendorDigest


def _digest(**overrides: object) -> VendorDigest:
    config = overrides.pop("config", None) or VendorConfig(
        name="turndown", ecosystem=Ecosystem.NPM, depth=Depth.SURFACE
    )
    defaults: dict[str, object] = {
        "config": config,
        "installed_version": "7.1.2",
        "api_surface": "TurndownService: converts HTML to Markdown.",
        "side_effects": [],
    }
    defaults.update(overrides)
    return VendorDigest(**defaults)  # type: ignore[arg-type]


def test_metadata_section_has_load_bearing_installed_version_line() -> None:
    markdown = render_vendor_claude_md(_digest(installed_version="7.1.2"))
    assert "- **Installed version:** 7.1.2" in markdown.splitlines()


def test_metadata_includes_ecosystem_and_depth() -> None:
    markdown = render_vendor_claude_md(_digest())
    assert "- **Ecosystem:** npm" in markdown.splitlines()
    assert "- **Depth:** surface" in markdown.splitlines()


def test_description_section_is_omitted() -> None:
    markdown = render_vendor_claude_md(_digest())
    assert "Description" not in markdown


def test_description_section_renders_technical_text_and_action_pointer() -> None:
    full_config = VendorConfig(name="turndown", ecosystem=Ecosystem.NPM, depth=Depth.FULL)
    markdown = render_vendor_claude_md(
        _digest(
            config=full_config,
            technical_description="TurndownService converts HTML to Markdown via rules.",
            action_pointer_file="src/commonmark-rules.js",
            action_pointer_note="override fencedCodeBlock here",
        )
    )
    assert "## Description" in markdown
    assert "TurndownService converts HTML to Markdown via rules." in markdown
    assert (
        "**Action pointer:** `src/commonmark-rules.js` — override fencedCodeBlock here"
        in markdown
    )


def test_description_section_omits_action_pointer_when_not_set() -> None:
    full_config = VendorConfig(name="turndown", ecosystem=Ecosystem.NPM, depth=Depth.FULL)
    markdown = render_vendor_claude_md(
        _digest(config=full_config, technical_description="Converts HTML to Markdown.")
    )
    assert "## Description" in markdown
    assert "Converts HTML to Markdown." in markdown
    assert "Action pointer" not in markdown


def test_description_section_shows_explicit_unavailable_note_on_failure() -> None:
    full_config = VendorConfig(name="turndown", ecosystem=Ecosystem.NPM, depth=Depth.FULL)
    markdown = render_vendor_claude_md(
        _digest(config=full_config, description_error="Anthropic API call failed: timeout")
    )
    assert "## Description" in markdown
    assert "_Description unavailable: `Anthropic API call failed: timeout`_" in markdown


def test_description_section_omitted_for_surface_vendor_even_with_error_set() -> None:
    """Since Phase 13, cloning (and therefore `description_error`) happens
    for every vendor, not just `depth = full` ones — a `depth = surface`
    vendor whose clone failed must not show a misleading "Description
    unavailable" note for an AI step it was never eligible for.
    """
    markdown = render_vendor_claude_md(
        _digest(description_error="git clone https://example.com/turndown failed: timeout")
    )
    assert "Description" not in markdown


def test_known_gotchas_from_side_effects() -> None:
    markdown = render_vendor_claude_md(
        _digest(side_effects=["npm postinstall script: node build.js"])
    )
    assert "- npm postinstall script: node build.js" in markdown.splitlines()


def test_known_gotchas_fallback_when_no_side_effects() -> None:
    markdown = render_vendor_claude_md(_digest(side_effects=[]))
    assert "No known side effects detected." in markdown.splitlines()


def test_quick_links_include_backlink_to_project_root() -> None:
    markdown = render_vendor_claude_md(_digest())
    assert "- [FILETREE.md](./FILETREE.md)" in markdown.splitlines()
    assert "- [DEPTREE.md](./DEPTREE.md)" in markdown.splitlines()
    assert "- [Project root CLAUDE.md](../../CLAUDE.md)" in markdown.splitlines()


def test_api_surface_fallback_when_none() -> None:
    markdown = render_vendor_claude_md(_digest(api_surface=None))
    assert "_No API surface extracted._" in markdown


def test_read_installed_version_finds_the_line(tmp_path: Path) -> None:
    claude_md_path = tmp_path / "CLAUDE.md"
    claude_md_path.write_text(
        "# turndown\n\n## Metadata\n\n- **Installed version:** 7.1.2\n", encoding="utf-8"
    )
    assert read_installed_version(claude_md_path) == "7.1.2"


def test_read_installed_version_none_when_file_missing(tmp_path: Path) -> None:
    assert read_installed_version(tmp_path / "CLAUDE.md") is None


def test_read_installed_version_none_when_line_missing(tmp_path: Path) -> None:
    claude_md_path = tmp_path / "CLAUDE.md"
    claude_md_path.write_text("# turndown\n\nhand-edited, no metadata\n", encoding="utf-8")
    assert read_installed_version(claude_md_path) is None


# --- read_enrichment_hash / update_description_section (Phase 14) -----------


def test_read_enrichment_hash_finds_the_line(tmp_path: Path) -> None:
    claude_md_path = tmp_path / "CLAUDE.md"
    claude_md_path.write_text(
        "# turndown\n\n## Metadata\n\n"
        "- **Installed version:** 7.1.2\n"
        "- **Enrichment symbol-set hash:** abc123\n",
        encoding="utf-8",
    )
    assert read_enrichment_hash(claude_md_path) == "abc123"


def test_read_enrichment_hash_none_when_file_missing(tmp_path: Path) -> None:
    assert read_enrichment_hash(tmp_path / "CLAUDE.md") is None


def test_read_enrichment_hash_none_when_line_missing(tmp_path: Path) -> None:
    claude_md_path = tmp_path / "CLAUDE.md"
    claude_md_path.write_text("# turndown\n\nhand-edited, no metadata\n", encoding="utf-8")
    assert read_enrichment_hash(claude_md_path) is None


def _surface_markdown(name: str = "turndown") -> str:
    """A `depth = surface` vendor's rendered `CLAUDE.md` — no Description
    section at all, the state `update_description_section` must be able to
    insert into, not just replace within.
    """
    config = VendorConfig(name=name, ecosystem=Ecosystem.NPM, depth=Depth.SURFACE)
    digest = VendorDigest(
        config=config, installed_version="7.1.2", api_surface="TurndownService API."
    )
    return render_vendor_claude_md(digest)


def test_update_description_section_inserts_a_new_section(tmp_path: Path) -> None:
    claude_md_path = tmp_path / "CLAUDE.md"
    claude_md_path.write_text(_surface_markdown(), encoding="utf-8")
    assert "## Description" not in claude_md_path.read_text(encoding="utf-8")

    update_description_section(
        claude_md_path,
        technical_description="TurndownService converts HTML via visitor rules.",
        action_pointer_file="src/commonmark-rules.js",
        action_pointer_note="override fencedCodeBlock here",
        symbol_set_hash="hash-123",
    )

    content = claude_md_path.read_text(encoding="utf-8")
    assert content.count("## Description") == 1
    assert "TurndownService converts HTML via visitor rules." in content
    assert (
        "**Action pointer:** `src/commonmark-rules.js` — override fencedCodeBlock here" in content
    )
    assert "- **Enrichment symbol-set hash:** hash-123" in content
    assert (
        content.index("## Public API surface")
        < content.index("## Description")
        < content.index("## Known gotchas")
    )


def test_update_description_section_omits_action_pointer_when_not_set(tmp_path: Path) -> None:
    claude_md_path = tmp_path / "CLAUDE.md"
    claude_md_path.write_text(_surface_markdown(), encoding="utf-8")

    update_description_section(
        claude_md_path,
        technical_description="Converts HTML to Markdown.",
        action_pointer_file=None,
        action_pointer_note=None,
        symbol_set_hash="hash-123",
    )

    content = claude_md_path.read_text(encoding="utf-8")
    assert "Converts HTML to Markdown." in content
    assert "Action pointer" not in content


def test_update_description_section_replaces_an_existing_section(tmp_path: Path) -> None:
    full_config = VendorConfig(name="turndown", ecosystem=Ecosystem.NPM, depth=Depth.FULL)
    old_digest = VendorDigest(
        config=full_config,
        installed_version="7.1.2",
        api_surface="API.",
        technical_description="OLD description.",
    )
    claude_md_path = tmp_path / "CLAUDE.md"
    claude_md_path.write_text(render_vendor_claude_md(old_digest), encoding="utf-8")

    update_description_section(
        claude_md_path,
        technical_description="NEW description.",
        action_pointer_file=None,
        action_pointer_note=None,
        symbol_set_hash="hash-456",
    )

    content = claude_md_path.read_text(encoding="utf-8")
    assert content.count("## Description") == 1
    assert "NEW description." in content
    assert "OLD description." not in content
    assert "Action pointer" not in content


def test_update_description_section_updates_hash_line_in_place_on_second_call(
    tmp_path: Path,
) -> None:
    claude_md_path = tmp_path / "CLAUDE.md"
    claude_md_path.write_text(_surface_markdown(), encoding="utf-8")

    update_description_section(
        claude_md_path,
        technical_description="v1",
        action_pointer_file=None,
        action_pointer_note=None,
        symbol_set_hash="hash-v1",
    )
    update_description_section(
        claude_md_path,
        technical_description="v2",
        action_pointer_file=None,
        action_pointer_note=None,
        symbol_set_hash="hash-v2",
    )

    content = claude_md_path.read_text(encoding="utf-8")
    assert content.count("**Enrichment symbol-set hash:**") == 1
    assert read_enrichment_hash(claude_md_path) == "hash-v2"
    assert "v1" not in content
    assert "v2" in content
    assert read_installed_version(claude_md_path) == "7.1.2"
