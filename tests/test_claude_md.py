from depcompass.claude_md import render_vendor_claude_md
from depcompass.core import Depth, Ecosystem, VendorConfig, VendorDigest


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


def test_gap_analysis_section_is_omitted() -> None:
    markdown = render_vendor_claude_md(_digest())
    assert "Gap analysis" not in markdown


def test_gap_analysis_section_renders_technical_text_and_action_pointer() -> None:
    full_config = VendorConfig(
        name="turndown", ecosystem=Ecosystem.NPM, depth=Depth.FULL, context_path="README.md"
    )
    markdown = render_vendor_claude_md(
        _digest(
            config=full_config,
            gap_analysis="The project uses fencedCodeBlock without overriding it.",
            action_pointer_file="src/commonmark-rules.js",
            action_pointer_note="override fencedCodeBlock here",
        )
    )
    assert "## Gap analysis" in markdown
    assert "The project uses fencedCodeBlock without overriding it." in markdown
    assert (
        "**Action pointer:** `src/commonmark-rules.js` — override fencedCodeBlock here"
        in markdown
    )


def test_gap_analysis_section_omits_action_pointer_when_not_set() -> None:
    full_config = VendorConfig(
        name="turndown", ecosystem=Ecosystem.NPM, depth=Depth.FULL, context_path="README.md"
    )
    markdown = render_vendor_claude_md(
        _digest(config=full_config, gap_analysis="No gaps found.")
    )
    assert "## Gap analysis" in markdown
    assert "No gaps found." in markdown
    assert "Action pointer" not in markdown


def test_gap_analysis_section_shows_explicit_unavailable_note_on_failure() -> None:
    full_config = VendorConfig(
        name="turndown", ecosystem=Ecosystem.NPM, depth=Depth.FULL, context_path="README.md"
    )
    markdown = render_vendor_claude_md(
        _digest(config=full_config, gap_analysis_error="Anthropic API call failed: timeout")
    )
    assert "## Gap analysis" in markdown
    assert "_Gap analysis unavailable: `Anthropic API call failed: timeout`_" in markdown


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
