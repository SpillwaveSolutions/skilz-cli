"""Integration tests for universal agent project-level support with custom config.

Tests SKILZ-50: Universal agent project-level installations with --config flag.
"""

import argparse
from unittest.mock import patch

from skilz.commands.install_cmd import cmd_install
from skilz.installer import install_local_skill
from skilz.manifest import read_manifest


class TestUniversalProjectInstall:
    """Test universal agent project-level installation scenarios."""

    def test_universal_project_install_default_config(self, tmp_path, monkeypatch):
        """Universal project install updates AGENTS.md by default."""
        # Setup: Create a project directory
        project_dir = tmp_path / "project"
        project_dir.mkdir()

        # Create universal skills directory
        skills_dir = project_dir / ".skilz" / "skills"
        skills_dir.mkdir(parents=True)

        # Create a test skill source
        skill_source = tmp_path / "test-skill"
        skill_source.mkdir()
        (skill_source / "SKILL.md").write_text("# Test Skill\n\nTest skill for universal agent.")

        # Change to project directory
        monkeypatch.chdir(project_dir)

        # Install skill with universal agent, project-level, no custom config
        with (
            patch("skilz.installer.detect_agent", return_value="universal"),
            patch("skilz.installer.ensure_skills_dir", return_value=skills_dir),
        ):
            install_local_skill(
                source_path=skill_source,
                agent="universal",
                project_level=True,
                verbose=False,
                force_config=False,
                config_file=None,  # Default behavior
            )

        # Verify: Skill installed to .skilz/skills/
        installed_skill = skills_dir / "test-skill"
        assert installed_skill.exists(), "Skill should be installed"
        assert (installed_skill / "SKILL.md").exists(), "SKILL.md should exist"

        # Verify: AGENTS.md was created by default
        agents_md = project_dir / "AGENTS.md"
        assert agents_md.exists(), "AGENTS.md should be created by default"

        content = agents_md.read_text()
        assert "test-skill" in content, "AGENTS.md should contain skill reference"

    def test_universal_project_install_custom_config(self, tmp_path, monkeypatch):
        """Universal project install with --config updates specified file."""
        # Setup: Create a project directory
        project_dir = tmp_path / "project"
        project_dir.mkdir()

        skills_dir = project_dir / ".skilz" / "skills"
        skills_dir.mkdir(parents=True)

        # Create a test skill source
        skill_source = tmp_path / "test-skill"
        skill_source.mkdir()
        (skill_source / "SKILL.md").write_text("# Test Skill\n\nTest skill with custom config.")

        # Change to project directory
        monkeypatch.chdir(project_dir)

        # Install with custom config file
        with (
            patch("skilz.installer.detect_agent", return_value="universal"),
            patch("skilz.installer.ensure_skills_dir", return_value=skills_dir),
        ):
            install_local_skill(
                source_path=skill_source,
                agent="universal",
                project_level=True,
                verbose=False,
                force_config=False,
                config_file="GEMINI.md",  # Custom config
            )

        # Verify: Skill installed to .skilz/skills/
        installed_skill = skills_dir / "test-skill"
        assert installed_skill.exists(), "Skill should be installed"

        # Verify: GEMINI.md was created (not AGENTS.md)
        gemini_md = project_dir / "GEMINI.md"
        assert gemini_md.exists(), "GEMINI.md should be created"

        content = gemini_md.read_text()
        assert "test-skill" in content, "GEMINI.md should contain skill reference"

        # Verify: AGENTS.md was NOT created
        agents_md = project_dir / "AGENTS.md"
        assert not agents_md.exists(), "AGENTS.md should NOT be created with --config"

    def test_config_flag_without_project_fails(self, tmp_path):
        """--config flag requires --project flag."""
        args = argparse.Namespace(
            skill_id="test/skill",
            agent="universal",
            project=False,  # Not project-level
            verbose=False,
            file=None,
            git=None,
            copy=False,
            symlink=False,
            version_spec=None,
            force_config=False,
            config="GEMINI.md",  # Has --config
        )

        # Should fail and return 1
        result = cmd_install(args)
        assert result == 1, "Install should fail without --project flag"

    def test_universal_custom_config_multiple_skills(self, tmp_path, monkeypatch):
        """Multiple skills can be installed with custom config."""
        # Setup: Create a project directory
        project_dir = tmp_path / "project"
        project_dir.mkdir()

        skills_dir = project_dir / ".skilz" / "skills"
        skills_dir.mkdir(parents=True)

        # Create two test skills
        skill1 = tmp_path / "skill1"
        skill1.mkdir()
        (skill1 / "SKILL.md").write_text("# Skill 1")

        skill2 = tmp_path / "skill2"
        skill2.mkdir()
        (skill2 / "SKILL.md").write_text("# Skill 2")

        # Change to project directory
        monkeypatch.chdir(project_dir)

        # Install first skill
        with (
            patch("skilz.installer.detect_agent", return_value="universal"),
            patch("skilz.installer.ensure_skills_dir", return_value=skills_dir),
        ):
            install_local_skill(
                source_path=skill1,
                agent="universal",
                project_level=True,
                verbose=False,
                force_config=False,
                config_file="CUSTOM.md",
            )

        # Install second skill
        with (
            patch("skilz.installer.detect_agent", return_value="universal"),
            patch("skilz.installer.ensure_skills_dir", return_value=skills_dir),
        ):
            install_local_skill(
                source_path=skill2,
                agent="universal",
                project_level=True,
                verbose=False,
                force_config=False,
                config_file="CUSTOM.md",
            )

        # Verify: Both skills in CUSTOM.md
        custom_md = project_dir / "CUSTOM.md"
        assert custom_md.exists(), "CUSTOM.md should exist"

        content = custom_md.read_text()
        assert "skill1" in content, "CUSTOM.md should contain skill1"
        assert "skill2" in content, "CUSTOM.md should contain skill2"

    def test_legacy_gemini_workflow(self, tmp_path, monkeypatch):
        """Legacy Gemini workflow (no experimental.skills plugin)."""
        # Setup: Project directory for legacy Gemini user
        project_dir = tmp_path / "project"
        project_dir.mkdir()

        # Universal skills directory (not .gemini/skills/)
        skills_dir = project_dir / ".skilz" / "skills"
        skills_dir.mkdir(parents=True)

        # Create a test skill
        skill_source = tmp_path / "pdf-reader"
        skill_source.mkdir()
        (skill_source / "SKILL.md").write_text("# PDF Reader\n\nRead PDFs.")

        # Change to project directory
        monkeypatch.chdir(project_dir)

        # Install with universal agent + GEMINI.md (legacy workflow)
        with (
            patch("skilz.installer.detect_agent", return_value="universal"),
            patch("skilz.installer.ensure_skills_dir", return_value=skills_dir),
        ):
            install_local_skill(
                source_path=skill_source,
                agent="universal",
                project_level=True,
                verbose=False,
                force_config=False,
                config_file="GEMINI.md",
            )

        # Verify: Installs to .skilz/skills/ (NOT .gemini/skills/)
        universal_dir = skills_dir / "pdf-reader"
        gemini_native_dir = project_dir / ".gemini" / "skills" / "pdf-reader"

        assert universal_dir.exists(), "Should install to .skilz/skills/"
        assert not gemini_native_dir.exists(), "Should NOT install to .gemini/skills/"

        # Verify: GEMINI.md is updated for Gemini CLI to read
        gemini_md = project_dir / "GEMINI.md"
        assert gemini_md.exists(), "GEMINI.md should be created"

        content = gemini_md.read_text()
        assert "pdf-reader" in content, "GEMINI.md should reference skill"

    def test_custom_config_with_arbitrary_filename(self, tmp_path, monkeypatch):
        """Custom config file with arbitrary filename works."""
        # Setup
        project_dir = tmp_path / "project"
        project_dir.mkdir()

        skills_dir = project_dir / ".skilz" / "skills"
        skills_dir.mkdir(parents=True)

        skill_source = tmp_path / "test-skill"
        skill_source.mkdir()
        (skill_source / "SKILL.md").write_text("# Test")

        monkeypatch.chdir(project_dir)

        # Install with completely custom filename
        with (
            patch("skilz.installer.detect_agent", return_value="universal"),
            patch("skilz.installer.ensure_skills_dir", return_value=skills_dir),
        ):
            install_local_skill(
                source_path=skill_source,
                agent="universal",
                project_level=True,
                verbose=False,
                force_config=False,
                config_file="MY_CUSTOM_SKILLS.md",
            )

        # Verify custom filename was created
        custom_file = project_dir / "MY_CUSTOM_SKILLS.md"
        assert custom_file.exists(), "Custom filename should be created"

        content = custom_file.read_text()
        assert "test-skill" in content, "Custom file should contain skill reference"

    def test_universal_config_file_updates_only_target(self, tmp_path, monkeypatch):
        """When --config is used, only the specified file is updated."""
        # Setup
        project_dir = tmp_path / "project"
        project_dir.mkdir()

        # Pre-create AGENTS.md
        agents_md = project_dir / "AGENTS.md"
        agents_md.write_text("# Existing AGENTS.md\n\nSome content")
        original_content = agents_md.read_text()

        skills_dir = project_dir / ".skilz" / "skills"
        skills_dir.mkdir(parents=True)

        skill_source = tmp_path / "test-skill"
        skill_source.mkdir()
        (skill_source / "SKILL.md").write_text("# Test")

        monkeypatch.chdir(project_dir)

        # Install with --config GEMINI.md
        with (
            patch("skilz.installer.detect_agent", return_value="universal"),
            patch("skilz.installer.ensure_skills_dir", return_value=skills_dir),
        ):
            install_local_skill(
                source_path=skill_source,
                agent="universal",
                project_level=True,
                verbose=False,
                force_config=False,
                config_file="GEMINI.md",
            )

        # Verify: GEMINI.md was updated
        gemini_md = project_dir / "GEMINI.md"
        assert gemini_md.exists(), "GEMINI.md should be created"
        assert "test-skill" in gemini_md.read_text()

        # Verify: AGENTS.md was NOT modified
        assert agents_md.exists(), "AGENTS.md should still exist"
        assert agents_md.read_text() == original_content, (
            "AGENTS.md should NOT be modified when using --config"
        )

    def test_universal_project_without_config_creates_agents_md(self, tmp_path, monkeypatch):
        """Universal project install without --config creates AGENTS.md."""
        # Setup
        project_dir = tmp_path / "project"
        project_dir.mkdir()

        skills_dir = project_dir / ".skilz" / "skills"
        skills_dir.mkdir(parents=True)

        skill_source = tmp_path / "test-skill"
        skill_source.mkdir()
        (skill_source / "SKILL.md").write_text("# Test")

        monkeypatch.chdir(project_dir)

        # Install without --config flag
        with (
            patch("skilz.installer.detect_agent", return_value="universal"),
            patch("skilz.installer.ensure_skills_dir", return_value=skills_dir),
        ):
            install_local_skill(
                source_path=skill_source,
                agent="universal",
                project_level=True,
                verbose=False,
                force_config=False,
                config_file=None,  # No custom config
            )

        # Verify: AGENTS.md was created (universal default)
        agents_md = project_dir / "AGENTS.md"
        assert agents_md.exists(), "AGENTS.md should be created by default"

        content = agents_md.read_text()
        assert "test-skill" in content, "AGENTS.md should contain skill"

        # Verify: No other config files created
        assert not (project_dir / "GEMINI.md").exists()
        assert not (project_dir / "CLAUDE.md").exists()

    def test_universal_manifest_created(self, tmp_path, monkeypatch):
        """Universal agent skills have proper manifest after install."""
        # Setup
        project_dir = tmp_path / "project"
        project_dir.mkdir()

        skills_dir = project_dir / ".skilz" / "skills"
        skills_dir.mkdir(parents=True)

        skill_source = tmp_path / "test-skill"
        skill_source.mkdir()
        (skill_source / "SKILL.md").write_text("# Test Skill")

        monkeypatch.chdir(project_dir)

        # Install with custom config
        with (
            patch("skilz.installer.detect_agent", return_value="universal"),
            patch("skilz.installer.ensure_skills_dir", return_value=skills_dir),
        ):
            install_local_skill(
                source_path=skill_source,
                agent="universal",
                project_level=True,
                verbose=False,
                force_config=False,
                config_file="GEMINI.md",
            )

        # Verify: Manifest exists
        installed_skill = skills_dir / "test-skill"
        manifest = read_manifest(installed_skill)

        assert manifest is not None, "Manifest should exist"
        assert manifest.git_repo == "local", "Local installs use 'local' as git_repo"
