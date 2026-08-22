import json
from pathlib import Path

import pytest
from typer.testing import CliRunner

import codecompass.cli as cli_module
from codecompass import enrichment, graph
from codecompass.cli import app
from codecompass.config import load_vendor_config
from codecompass.core import VendorDigest

runner = CliRunner()


def test_init_creates_parseable_vendor_toml(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.chdir(tmp_path)
    (tmp_path / "package.json").write_text(
        json.dumps({"dependencies": {"lodash": "^4.0.0"}}), encoding="utf-8"
    )

    result = runner.invoke(app, ["init", "--scan", "package.json"])

    assert result.exit_code == 0, result.output
    vendors = load_vendor_config(tmp_path / "vendor.toml")
    assert [v.name for v in vendors] == ["lodash"]


def test_init_errors_when_vendor_toml_already_exists(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.chdir(tmp_path)
    (tmp_path / "package.json").write_text(
        json.dumps({"dependencies": {"lodash": "^4.0.0"}}), encoding="utf-8"
    )
    (tmp_path / "vendor.toml").write_text("# hand-edited\n", encoding="utf-8")

    result = runner.invoke(app, ["init", "--scan", "package.json"])

    assert result.exit_code == 1
    assert "already exists" in result.output
    assert (tmp_path / "vendor.toml").read_text(encoding="utf-8") == "# hand-edited\n"


def test_bare_bootstrap_creates_vendor_toml_and_syncs_new_vendors(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.chdir(tmp_path)
    (tmp_path / "requirements.txt").write_text("pytest\n", encoding="utf-8")

    result = runner.invoke(app, [])

    assert result.exit_code == 0, result.output
    vendors = load_vendor_config(tmp_path / "vendor.toml")
    assert [v.name for v in vendors] == ["pytest"]
    assert (tmp_path / "vendor" / "pytest" / "CLAUDE.md").exists()
    assert "<!-- codecompass:start -->" in (tmp_path / "CLAUDE.md").read_text(encoding="utf-8")
    assert (tmp_path / ".claude" / "skills" / "codecompass" / "SKILL.md").exists()
    assert (tmp_path / ".claude" / "commands" / "discovery.md").exists()


def test_bare_bootstrap_no_manifests_creates_empty_vendor_toml(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.chdir(tmp_path)

    result = runner.invoke(app, [])

    assert result.exit_code == 0, result.output
    assert load_vendor_config(tmp_path / "vendor.toml") == []


def test_bare_bootstrap_refresh_leaves_existing_full_vendor_untouched(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.chdir(tmp_path)
    (tmp_path / "vendor.toml").write_text(
        '[[vendor]]\nname = "pytest"\necosystem = "python"\ndepth = "full"\n',
        encoding="utf-8",
    )
    (tmp_path / "requirements.txt").write_text("pytest\nrich\n", encoding="utf-8")

    synced_names: list[str] = []

    def _fake_sync_all(configs, project_root):  # noqa: ANN001
        synced_names.extend(c.name for c in configs)
        return [VendorDigest(config=c, installed_version="1.0.0") for c in configs]

    monkeypatch.setattr(cli_module, "sync_all", _fake_sync_all)

    result = runner.invoke(app, [])

    assert result.exit_code == 0, result.output
    # Only the newly-discovered "rich" is synced — "pytest" was already
    # tracked and is left untouched, so this command never pays AI cost
    # (decisions/0017).
    assert synced_names == ["rich"]
    vendors = {v.name: v for v in load_vendor_config(tmp_path / "vendor.toml")}
    assert set(vendors) == {"pytest", "rich"}


def test_bare_bootstrap_second_run_is_a_noop_when_nothing_new(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.chdir(tmp_path)
    (tmp_path / "requirements.txt").write_text("pytest\n", encoding="utf-8")

    first = runner.invoke(app, [])
    assert first.exit_code == 0, first.output
    second = runner.invoke(app, [])
    assert second.exit_code == 0, second.output

    vendors = load_vendor_config(tmp_path / "vendor.toml")
    assert [v.name for v in vendors] == ["pytest"]


def test_sync_all_vendors_end_to_end_real_python_adapter(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Real end-to-end run against an already-installed package (pytest),
    same live-package pattern as Phase 2's adapter smoke tests — no
    mocking of sync/adapters here.
    """
    monkeypatch.chdir(tmp_path)
    (tmp_path / "vendor.toml").write_text(
        '[[vendor]]\nname = "pytest"\necosystem = "python"\ndepth = "surface"\n',
        encoding="utf-8",
    )

    result = runner.invoke(app, ["sync"])

    assert result.exit_code == 0, result.output
    assert (tmp_path / "vendor" / "pytest" / "CLAUDE.md").exists()
    assert (tmp_path / "vendor" / "pytest" / "FILETREE.md").exists()


def test_sync_unknown_vendor_name_errors(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.chdir(tmp_path)
    (tmp_path / "vendor.toml").write_text(
        '[[vendor]]\nname = "pytest"\necosystem = "python"\ndepth = "surface"\n',
        encoding="utf-8",
    )

    result = runner.invoke(app, ["sync", "not-a-real-vendor"])

    assert result.exit_code == 1
    assert "not found in vendor.toml" in result.output


def test_sync_single_vendor_filters_by_name(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.chdir(tmp_path)
    (tmp_path / "vendor.toml").write_text(
        '[[vendor]]\nname = "a"\necosystem = "python"\ndepth = "surface"\n\n'
        '[[vendor]]\nname = "b"\necosystem = "python"\ndepth = "surface"\n',
        encoding="utf-8",
    )
    synced_names: list[str] = []

    def _fake_sync_all(configs, project_root):  # noqa: ANN001
        synced_names.extend(c.name for c in configs)
        return [VendorDigest(config=c, installed_version="1.0.0") for c in configs]

    monkeypatch.setattr(cli_module, "sync_all", _fake_sync_all)

    result = runner.invoke(app, ["sync", "a"])

    assert result.exit_code == 0, result.output
    assert synced_names == ["a"]


def test_sync_reports_description_failure_and_exits_nonzero(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.chdir(tmp_path)
    (tmp_path / "vendor.toml").write_text(
        '[[vendor]]\nname = "turndown"\necosystem = "npm"\n',
        encoding="utf-8",
    )

    def _fake_sync_all(configs, project_root):  # noqa: ANN001
        return [
            VendorDigest(
                config=c,
                installed_version="1.0.0",
                description_error="Anthropic API call failed: timeout",
            )
            for c in configs
        ]

    monkeypatch.setattr(cli_module, "sync_all", _fake_sync_all)
    # Whole-project `sync` also rebuilds context-graph.db (Phase 11), which
    # needs a real adapter for "turndown" — not installed in this fixture
    # and irrelevant to what this test actually verifies (the CLI's
    # digest-error reporting), so it's stubbed out here too.
    monkeypatch.setattr(cli_module, "rebuild_project_graph", lambda configs, project_root: None)

    result = runner.invoke(app, ["sync"])

    assert result.exit_code == 1
    assert "description failed" in result.output
    assert "timeout" in result.output


def test_sync_whole_project_phase_b_yes_flag_enriches(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.chdir(tmp_path)
    (tmp_path / "vendor.toml").write_text(
        '[[vendor]]\nname = "pytest"\necosystem = "python"\ndepth = "surface"\n',
        encoding="utf-8",
    )

    def _fake_select_candidates(conn, configs, project_root):  # noqa: ANN001
        (config,) = configs
        return [_fake_enrichment_candidate(config)]

    def _fake_run_enrichment_batches(candidates):  # noqa: ANN001
        return [_fake_enrichment_result("pytest")]

    monkeypatch.setattr("codecompass.enrichment.select_candidates", _fake_select_candidates)
    monkeypatch.setattr(
        "codecompass.enrichment.run_enrichment_batches", _fake_run_enrichment_batches
    )

    result = runner.invoke(app, ["sync", "--yes"])

    assert result.exit_code == 0, result.output
    assert (tmp_path / ".claude" / "skills" / "codecompass-pytest" / "SKILL.md").exists()


def test_sync_single_vendor_never_triggers_phase_b(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """`sync <vendor>` is the single-vendor branch — no graph rebuild, no
    enrichment trigger (decisions/0025).
    """
    monkeypatch.chdir(tmp_path)
    (tmp_path / "vendor.toml").write_text(
        '[[vendor]]\nname = "pytest"\necosystem = "python"\ndepth = "surface"\n',
        encoding="utf-8",
    )
    called: list[bool] = []
    monkeypatch.setattr(
        "codecompass.enrichment.select_candidates",
        lambda *a, **k: called.append(True) or [],  # noqa: ANN001
    )

    result = runner.invoke(app, ["sync", "pytest"])

    assert result.exit_code == 0, result.output
    assert not called


def test_sync_whole_project_zero_candidates_still_refreshes_routing_table(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Regression for gap 2 (planning/phase-20-refresh-generated-artifacts-
    after-enrichment.md): before this phase, `sync`'s whole-project branch
    never called `update_root_claude_md`/`write_tool_skill`/
    `write_discovery_command` at all — only `index` or `_bootstrap` did.
    A whole-project `sync` with zero enrichment candidates (no `--yes`, no
    fixture that triggers Phase B — the common case) must still refresh
    them at least once, without a separate `codecompass index`.
    """
    monkeypatch.chdir(tmp_path)
    (tmp_path / "vendor.toml").write_text(
        '[[vendor]]\nname = "pytest"\necosystem = "python"\ndepth = "surface"\n',
        encoding="utf-8",
    )

    result = runner.invoke(app, ["sync"])

    assert result.exit_code == 0, result.output
    assert "<!-- codecompass:start -->" in (tmp_path / "CLAUDE.md").read_text(encoding="utf-8")
    assert (tmp_path / ".claude" / "skills" / "codecompass" / "SKILL.md").exists()
    assert (tmp_path / ".claude" / "commands" / "discovery.md").exists()


def test_undo_dry_run_sees_per_vendor_skill_immediately_after_enrichment(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Regression for the `undo`-freshness symptom this phase also closes:
    both gaps meant `context-graph.db` didn't know about a Skill Phase B
    just wrote (`skill_scan.scan_skills` hadn't re-run since) until a
    separate whole-project sync — so `undo`'s graph-backed enumeration
    (`_graph_backed_undo_paths`) missed a vendor's brand-new per-vendor
    Skill at this exact point, right after the triggering enrichment run.
    """
    monkeypatch.chdir(tmp_path)
    (tmp_path / "requirements.txt").write_text("pytest\n", encoding="utf-8")

    def _fake_select_candidates(conn, configs, project_root):  # noqa: ANN001
        (config,) = [c for c in configs if c.name == "pytest"]
        return [_fake_enrichment_candidate(config)]

    def _fake_run_enrichment_batches(candidates):  # noqa: ANN001
        return [_fake_enrichment_result("pytest")]

    monkeypatch.setattr("codecompass.enrichment.select_candidates", _fake_select_candidates)
    monkeypatch.setattr(
        "codecompass.enrichment.run_enrichment_batches", _fake_run_enrichment_batches
    )

    bootstrap_result = runner.invoke(app, ["--yes"])
    assert bootstrap_result.exit_code == 0, bootstrap_result.output

    result = runner.invoke(app, ["undo", "--dry-run"])

    assert result.exit_code == 0, result.output
    assert ".claude/skills/codecompass-pytest" in result.output


def test_index_injects_routing_table_into_root_claude_md(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.chdir(tmp_path)
    (tmp_path / "vendor.toml").write_text(
        '[[vendor]]\nname = "turndown"\necosystem = "npm"\ndepth = "surface"\n',
        encoding="utf-8",
    )
    vendor_dir = tmp_path / "vendor" / "turndown"
    vendor_dir.mkdir(parents=True)
    (vendor_dir / "CLAUDE.md").write_text(
        "# turndown\n\n## Metadata\n\n- **Installed version:** 7.1.2\n", encoding="utf-8"
    )
    (tmp_path / "CLAUDE.md").write_text("# My Project\n", encoding="utf-8")

    result = runner.invoke(app, ["index"])

    assert result.exit_code == 0, result.output
    root_claude_md = (tmp_path / "CLAUDE.md").read_text(encoding="utf-8")
    assert "turndown" in root_claude_md
    assert "7.1.2" in root_claude_md
    assert "<!-- codecompass:start -->" in root_claude_md
    assert (tmp_path / ".claude" / "skills" / "codecompass" / "SKILL.md").exists()
    assert (tmp_path / ".claude" / "commands" / "discovery.md").exists()


def test_index_regenerates_discovery_command_after_manual_deletion(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Same idempotent regeneration guarantee every other generated
    artifact already has (plan verification step).
    """
    monkeypatch.chdir(tmp_path)
    (tmp_path / "vendor.toml").write_text(
        '[[vendor]]\nname = "turndown"\necosystem = "npm"\ndepth = "surface"\n',
        encoding="utf-8",
    )
    vendor_dir = tmp_path / "vendor" / "turndown"
    vendor_dir.mkdir(parents=True)
    (vendor_dir / "CLAUDE.md").write_text(
        "# turndown\n\n## Metadata\n\n- **Installed version:** 7.1.2\n", encoding="utf-8"
    )
    (tmp_path / "CLAUDE.md").write_text("# My Project\n", encoding="utf-8")
    runner.invoke(app, ["index"])
    discovery_md = tmp_path / ".claude" / "commands" / "discovery.md"
    assert discovery_md.exists()
    discovery_md.unlink()

    result = runner.invoke(app, ["index"])

    assert result.exit_code == 0, result.output
    assert discovery_md.exists()


def test_promote_command_removed(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """`promote` is retired entirely (decisions/0033, Phase 15) — its three
    former jobs (clone, enrich, generate Skill) are now automatic outcomes
    of bootstrap/`sync`. Typer's standard "no such command" error, not a
    traceback.
    """
    monkeypatch.chdir(tmp_path)

    result = runner.invoke(app, ["promote", "anything"])

    assert result.exit_code != 0
    assert "no such command" in result.output.lower()


def _fake_enrichment_candidate(config, **overrides):  # noqa: ANN001
    defaults = {
        "vendor": config,
        "used_symbol_names": [],
        "material": "# fake\n\nSome material.",
        "installed_version": "1.0.0",
    }
    defaults.update(overrides)
    return enrichment.EnrichmentCandidate(**defaults)


def _fake_enrichment_result(vendor_name: str, **overrides):  # noqa: ANN001
    defaults = {
        "vendor": vendor_name,
        "technical_description": "Does a thing.",
        "conversational_overview": "A thing-doer.",
        "symbol_purposes": {},
        "symbol_set_hash": "fake-hash",
    }
    defaults.update(overrides)
    return enrichment.EnrichmentResult(**defaults)


def test_bare_bootstrap_phase_b_yes_flag_enriches_without_prompting(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.chdir(tmp_path)
    (tmp_path / "requirements.txt").write_text("pytest\n", encoding="utf-8")

    def _fake_select_candidates(conn, configs, project_root):  # noqa: ANN001
        (config,) = [c for c in configs if c.name == "pytest"]
        return [_fake_enrichment_candidate(config)]

    def _fake_run_enrichment_batches(candidates):  # noqa: ANN001
        return [_fake_enrichment_result("pytest")]

    monkeypatch.setattr("codecompass.enrichment.select_candidates", _fake_select_candidates)
    monkeypatch.setattr(
        "codecompass.enrichment.run_enrichment_batches", _fake_run_enrichment_batches
    )

    result = runner.invoke(app, ["--yes"])

    assert result.exit_code == 0, result.output
    assert "enriched" in result.output
    assert (tmp_path / ".claude" / "skills" / "codecompass-pytest" / "SKILL.md").exists()
    assert (tmp_path / ".cursor" / "rules" / "codecompass-pytest.mdc").exists()


def test_bare_bootstrap_phase_b_enrichment_refreshes_routing_table_same_invocation(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Regression for gap 1 (planning/phase-20-refresh-generated-artifacts-
    after-enrichment.md): before this phase, the routing table and
    tool-level Skill were regenerated *before* Phase B ran, so a vendor
    enriched in this same invocation still showed `Enriched: no` until a
    separate `codecompass index`. Both must show post-enrichment status
    without a follow-up command.
    """
    monkeypatch.chdir(tmp_path)
    (tmp_path / "requirements.txt").write_text("pytest\n", encoding="utf-8")

    def _fake_select_candidates(conn, configs, project_root):  # noqa: ANN001
        (config,) = [c for c in configs if c.name == "pytest"]
        return [_fake_enrichment_candidate(config)]

    def _fake_run_enrichment_batches(candidates):  # noqa: ANN001
        return [_fake_enrichment_result("pytest")]

    monkeypatch.setattr("codecompass.enrichment.select_candidates", _fake_select_candidates)
    monkeypatch.setattr(
        "codecompass.enrichment.run_enrichment_batches", _fake_run_enrichment_batches
    )

    result = runner.invoke(app, ["--yes"])

    assert result.exit_code == 0, result.output
    root_claude_md = (tmp_path / "CLAUDE.md").read_text(encoding="utf-8")
    # `render_routing_table` only emits this "consult when" text for a row
    # it considers enriched (`_CONSULT_WHEN_BY_ENRICHED[True]`) — its
    # presence is proof the routing table was rendered *after* Phase B
    # applied its results, not before.
    assert "API questions and known gotchas" in root_claude_md
    tool_skill_md = (tmp_path / ".claude" / "skills" / "codecompass" / "SKILL.md").read_text(
        encoding="utf-8"
    )
    assert "| pytest | python | yes |" in tool_skill_md


def test_bare_bootstrap_phase_b_declined_confirmation_skips_enrichment(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.chdir(tmp_path)
    (tmp_path / "requirements.txt").write_text("pytest\n", encoding="utf-8")

    def _fake_select_candidates(conn, configs, project_root):  # noqa: ANN001
        (config,) = [c for c in configs if c.name == "pytest"]
        return [_fake_enrichment_candidate(config)]

    called: list[bool] = []
    monkeypatch.setattr("codecompass.enrichment.select_candidates", _fake_select_candidates)
    monkeypatch.setattr(
        "codecompass.enrichment.run_enrichment_batches",
        lambda candidates: called.append(True) or [],  # noqa: ANN001
    )

    result = runner.invoke(app, [], input="n\n")

    assert result.exit_code == 0, result.output
    assert not called
    assert "skipped" in result.output
    # Phase A output still exists — declining Phase B doesn't undo it.
    assert (tmp_path / "vendor" / "pytest" / "CLAUDE.md").exists()
    assert not (tmp_path / ".claude" / "skills" / "codecompass-pytest" / "SKILL.md").exists()


def test_bare_bootstrap_phase_b_budget_too_low_exits_nonzero_but_keeps_phase_a(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.chdir(tmp_path)
    (tmp_path / "requirements.txt").write_text("pytest\n", encoding="utf-8")

    def _fake_select_candidates(conn, configs, project_root):  # noqa: ANN001
        (config,) = [c for c in configs if c.name == "pytest"]
        return [_fake_enrichment_candidate(config)]

    monkeypatch.setattr("codecompass.enrichment.select_candidates", _fake_select_candidates)

    result = runner.invoke(app, ["--budget", "0"])

    assert result.exit_code == 1
    # Two separate substring checks, not one contiguous phrase — Rich
    # word-wraps long console lines at the terminal width, which can (and
    # here does) insert a line break between "exceeds" and "--budget".
    assert "exceeds" in result.output
    assert "--budget" in result.output
    # Phase A's free work already completed before Phase B's budget check.
    assert (tmp_path / "vendor" / "pytest" / "CLAUDE.md").exists()
    assert "<!-- codecompass:start -->" in (tmp_path / "CLAUDE.md").read_text(encoding="utf-8")


def test_bare_bootstrap_no_enrichment_candidates_never_prompts(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """No usage-proven vendors (the common case for these fixtures — no
    real project source imports anything) means `select_candidates`
    returns `[]` and Phase B is a silent no-op — this is what lets nearly
    every other bootstrap test invoke `codecompass` with no `--yes` and
    never risk a real Anthropic API call (decisions/0016).
    """
    monkeypatch.chdir(tmp_path)
    (tmp_path / "requirements.txt").write_text("pytest\n", encoding="utf-8")

    result = runner.invoke(app, [])

    assert result.exit_code == 0, result.output
    assert "enrichment" not in result.output


def test_check_bare_always_exits_0_even_with_major_delta(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.chdir(tmp_path)
    _write_vendor_toml_and_synced_claude_md(tmp_path, recorded="1.0.0")
    monkeypatch.setattr(
        "codecompass.staleness.get_adapter",
        lambda config, project_root: _FakeStalenessAdapter(version="2.0.0"),
    )

    result = runner.invoke(app, ["check"])

    assert result.exit_code == 0, result.output
    assert "major" in result.output


def _write_vendor_toml_and_synced_claude_md(
    tmp_path: Path, *, name: str = "demo", ecosystem: str = "python", recorded: str = "1.0.0"
) -> None:
    (tmp_path / "vendor.toml").write_text(
        f'[[vendor]]\nname = "{name}"\necosystem = "{ecosystem}"\ndepth = "surface"\n',
        encoding="utf-8",
    )
    vendor_dir = tmp_path / "vendor" / name
    vendor_dir.mkdir(parents=True)
    (vendor_dir / "CLAUDE.md").write_text(
        f"# {name}\n\n## Metadata\n\n- **Installed version:** {recorded}\n", encoding="utf-8"
    )


def test_check_strict_exits_1_on_major_delta(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.chdir(tmp_path)
    _write_vendor_toml_and_synced_claude_md(tmp_path, recorded="1.0.0")
    monkeypatch.setattr(
        "codecompass.staleness.get_adapter",
        lambda config, project_root: _FakeStalenessAdapter(version="2.0.0"),
    )

    result = runner.invoke(app, ["check", "--strict"])

    assert result.exit_code == 1


def test_check_strict_exits_0_on_minor_or_patch_only(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.chdir(tmp_path)
    _write_vendor_toml_and_synced_claude_md(tmp_path, recorded="1.0.0")
    monkeypatch.setattr(
        "codecompass.staleness.get_adapter",
        lambda config, project_root: _FakeStalenessAdapter(version="1.1.0"),
    )

    result = runner.invoke(app, ["check", "--strict"])

    assert result.exit_code == 0, result.output


def test_check_strict_and_fix_together_errors(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.chdir(tmp_path)
    _write_vendor_toml_and_synced_claude_md(tmp_path)

    result = runner.invoke(app, ["check", "--strict", "--fix"])

    assert result.exit_code == 1
    assert "mutually exclusive" in result.output


def test_check_fix_regenerates_stale_vendor_and_exits_0(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.chdir(tmp_path)
    _write_vendor_toml_and_synced_claude_md(tmp_path, recorded="1.0.0")
    monkeypatch.setattr(
        "codecompass.staleness.get_adapter",
        lambda config, project_root: _FakeStalenessAdapter(version="2.0.0"),
    )
    monkeypatch.setattr(
        cli_module,
        "sync_vendor",
        lambda config, project_root: VendorDigest(config=config, installed_version="2.0.0"),
    )

    result = runner.invoke(app, ["check", "--fix"])

    assert result.exit_code == 0, result.output
    assert "fixed" in result.output


def test_check_fix_isolates_one_vendor_adapter_failure(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.chdir(tmp_path)
    (tmp_path / "vendor.toml").write_text(
        '[[vendor]]\nname = "a"\necosystem = "python"\ndepth = "surface"\n\n'
        '[[vendor]]\nname = "b"\necosystem = "python"\ndepth = "surface"\n',
        encoding="utf-8",
    )
    for name in ("a", "b"):
        vendor_dir = tmp_path / "vendor" / name
        vendor_dir.mkdir(parents=True)
        (vendor_dir / "CLAUDE.md").write_text(
            f"# {name}\n\n## Metadata\n\n- **Installed version:** 1.0.0\n", encoding="utf-8"
        )

    monkeypatch.setattr(
        "codecompass.staleness.get_adapter",
        lambda config, project_root: _FakeStalenessAdapter(version="2.0.0"),
    )
    fixed: list[str] = []

    def _fake_sync_vendor(config, project_root):  # noqa: ANN001
        if config.name == "a":
            raise cli_module.AdapterError("a is broken")
        fixed.append(config.name)
        return VendorDigest(config=config, installed_version="2.0.0")

    monkeypatch.setattr(cli_module, "sync_vendor", _fake_sync_vendor)

    result = runner.invoke(app, ["check", "--fix"])

    assert result.exit_code == 1
    assert fixed == ["b"]
    assert "fix failed" in result.output


def test_check_without_graph_prints_note_and_still_exits_0(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.chdir(tmp_path)
    _write_vendor_toml_and_synced_claude_md(tmp_path, recorded="1.0.0")
    monkeypatch.setattr(
        "codecompass.staleness.get_adapter",
        lambda config, project_root: _FakeStalenessAdapter(version="1.0.0"),
    )

    result = runner.invoke(app, ["check"])

    assert result.exit_code == 0, result.output
    assert "context-graph.db" in result.output


def _rebuild_empty_graph(project_root: Path, vendor_names: list[str]) -> None:
    conn = graph.open_graph(project_root)
    graph.rebuild_deterministic(
        conn,
        vendors=[graph.VendorRow(name=name, ecosystem="python") for name in vendor_names],
        source_files=[],
        symbols=[],
        uses_edges=[],
        doc_artifacts=[],
        documents_edges=[],
        skill_mentions_edges=[],
        routes_via_edges=[],
        depends_on_edges=[],
    )
    conn.close()


def test_check_reports_unused_vendor_section_when_graph_exists(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.chdir(tmp_path)
    _write_vendor_toml_and_synced_claude_md(tmp_path, name="demo", recorded="1.0.0")
    monkeypatch.setattr(
        "codecompass.staleness.get_adapter",
        lambda config, project_root: _FakeStalenessAdapter(version="1.0.0"),
    )
    _rebuild_empty_graph(tmp_path, ["demo"])  # zero uses_edges — unused by construction

    result = runner.invoke(app, ["check"])

    assert result.exit_code == 0, result.output
    assert "Unused vendors" in result.output
    assert "demo" in result.output


def test_check_strict_exit_code_unaffected_by_coverage_gaps(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A real coverage gap (an unused vendor present in the graph) must not
    flip `--strict`'s exit code — it stays governed by version-drift
    severity alone (confirmed twice during this rework's planning
    interview, per planning/phase-15-cli-rewire.md's Design decisions).
    """
    monkeypatch.chdir(tmp_path)
    _write_vendor_toml_and_synced_claude_md(tmp_path, name="demo", recorded="1.0.0")
    monkeypatch.setattr(
        "codecompass.staleness.get_adapter",
        lambda config, project_root: _FakeStalenessAdapter(version="1.0.0"),
    )
    _rebuild_empty_graph(tmp_path, ["demo"])

    result = runner.invoke(app, ["check", "--strict"])

    assert result.exit_code == 0, result.output
    assert "demo" in result.output


class _FakeStalenessAdapter:
    def __init__(self, *, version: str, error: Exception | None = None) -> None:
        self._version = version
        self._error = error

    def installed_version(self) -> str:
        if self._error is not None:
            raise self._error
        return self._version

    def dependency_tree(self):  # noqa: ANN201
        from codecompass.core import DepNode

        return DepNode(name="demo", version=self._version)


# --- query command group ------------------------------------------------


def test_query_vendors_without_graph_prints_note(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.chdir(tmp_path)

    result = runner.invoke(app, ["query", "vendors"])

    assert result.exit_code == 0, result.output
    assert "sync" in result.output.lower()


def test_query_vendor_without_graph_prints_note(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.chdir(tmp_path)

    result = runner.invoke(app, ["query", "vendor", "demo"])

    assert result.exit_code == 0, result.output
    assert "sync" in result.output.lower()


def test_query_symbol_without_graph_prints_note(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.chdir(tmp_path)

    result = runner.invoke(app, ["query", "symbol", "doStuff"])

    assert result.exit_code == 0, result.output
    assert "sync" in result.output.lower()


def test_query_skills_without_graph_prints_note(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.chdir(tmp_path)

    result = runner.invoke(app, ["query", "skills"])

    assert result.exit_code == 0, result.output
    assert "sync" in result.output.lower()


def _build_query_fixture(project_root: Path) -> None:
    conn = graph.open_graph(project_root)
    graph.rebuild_deterministic(
        conn,
        vendors=[
            graph.VendorRow(name="used-lib", ecosystem="npm", installed_version="1.2.3"),
            graph.VendorRow(name="unused-lib", ecosystem="python", installed_version="0.1.0"),
        ],
        source_files=[graph.SourceFileRow(path="src/app.ts")],
        symbols=[graph.SymbolRow(vendor_name="used-lib", name="doStuff", purpose="does stuff")],
        uses_edges=[
            graph.UsesEdgeRow(
                source_file_path="src/app.ts",
                vendor_name="used-lib",
                symbol_name="doStuff",
                line=1,
            )
        ],
        doc_artifacts=[],
        documents_edges=[],
        skill_mentions_edges=[],
        routes_via_edges=[],
        depends_on_edges=[],
    )
    conn.close()


def test_query_vendors_lists_every_tracked_vendor(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.chdir(tmp_path)
    _build_query_fixture(tmp_path)

    result = runner.invoke(app, ["query", "vendors"])

    assert result.exit_code == 0, result.output
    assert "used-lib" in result.output
    assert "unused-lib" in result.output


def test_query_vendors_unused_filters_to_unused_only(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # "used-lib" and "unused-lib" are both vendor names below (the latter
    # containing the former as a substring), so this asserts on parsed
    # JSON rather than a raw-output substring check.
    monkeypatch.chdir(tmp_path)
    _build_query_fixture(tmp_path)

    result = runner.invoke(app, ["query", "vendors", "--unused", "--json"])

    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    names = {entry["name"] for entry in payload}
    assert names == {"unused-lib"}


def test_query_vendors_json_outputs_parseable_json(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.chdir(tmp_path)
    _build_query_fixture(tmp_path)

    result = runner.invoke(app, ["query", "vendors", "--json"])

    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    names = {entry["name"] for entry in payload}
    assert names == {"used-lib", "unused-lib"}


def test_query_vendor_returns_profile(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.chdir(tmp_path)
    _build_query_fixture(tmp_path)

    result = runner.invoke(app, ["query", "vendor", "used-lib"])

    assert result.exit_code == 0, result.output
    assert "used-lib" in result.output
    assert "doStuff" in result.output


def test_query_vendor_unknown_name_errors(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.chdir(tmp_path)
    _build_query_fixture(tmp_path)

    result = runner.invoke(app, ["query", "vendor", "does-not-exist"])

    assert result.exit_code == 1
    assert "not found" in result.output


def test_query_symbol_returns_matches_across_vendors(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.chdir(tmp_path)
    _build_query_fixture(tmp_path)

    result = runner.invoke(app, ["query", "symbol", "doStuff"])

    assert result.exit_code == 0, result.output
    assert "used-lib" in result.output


def test_query_skills_lists_skill_artifacts(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.chdir(tmp_path)
    conn = graph.open_graph(tmp_path)
    graph.rebuild_deterministic(
        conn,
        vendors=[],
        source_files=[],
        symbols=[],
        uses_edges=[],
        doc_artifacts=[
            graph.DocArtifactRow(
                path=".claude/skills/third-party/SKILL.md",
                kind="skill",
                origin="third_party",
                name="third-party",
            )
        ],
        documents_edges=[],
        skill_mentions_edges=[],
        routes_via_edges=[],
        depends_on_edges=[],
    )
    conn.close()

    result = runner.invoke(app, ["query", "skills", "--json"])

    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert [entry["name"] for entry in payload] == ["third-party"]


def test_query_skills_unused_mentions_filters_to_orphaned_skills(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.chdir(tmp_path)
    conn = graph.open_graph(tmp_path)
    graph.rebuild_deterministic(
        conn,
        vendors=[graph.VendorRow(name="used-lib", ecosystem="npm")],
        source_files=[],
        symbols=[],
        uses_edges=[],
        doc_artifacts=[
            graph.DocArtifactRow(
                path=".claude/skills/orphan/SKILL.md",
                kind="skill",
                origin="third_party",
                name="orphan",
            ),
            graph.DocArtifactRow(
                path=".claude/skills/mentions-vendor/SKILL.md",
                kind="skill",
                origin="third_party",
                name="mentions-vendor",
            ),
        ],
        documents_edges=[],
        skill_mentions_edges=[
            graph.SkillMentionEdgeRow(
                doc_artifact_path=".claude/skills/mentions-vendor/SKILL.md",
                vendor_name="used-lib",
            )
        ],
        routes_via_edges=[],
        depends_on_edges=[],
    )
    conn.close()

    result = runner.invoke(app, ["query", "skills", "--unused-mentions", "--json"])

    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert [entry["name"] for entry in payload] == ["orphan"]
