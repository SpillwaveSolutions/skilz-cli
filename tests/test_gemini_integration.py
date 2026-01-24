"""Integration tests for Gemini CLI native skill support (SKILZ-49)."""

from pathlib import Path
from unittest.mock import patch

import pytest

from skilz.agents import detect_agent
from skilz.installer import install_local_skill
from skilz.manifest import read_manifest


class TestGeminiNativeInstall:
    """Test Gemini native skill installation scenarios."""

    def test_install_skill_to_gemini_native_project(self, tmp_path, monkeypatch):
        """Install skill to Gemini project-level (.gemini/skills/) without config sync."""
        # Setup: Create a Gemini project structure
        project_dir = tmp_path / "project"
        project_dir.mkdir()
        target_root = project_dir / ".gemini" / "skills"
        target_root.mkdir(parents=True)

        # Create a test skill source
        skill_source = tmp_path / "test-skill"
        skill_source.mkdir()
        (skill_source / "SKILL.md").write_text("# Test Skill\nA test skill.")

        # Change to project directory
        monkeypatch.chdir(project_dir)

        # Install skill with mocked detection and ensure_skills_dir
        with (
            patch("skilz.installer.detect_agent", return_value="gemini"),
            patch("skilz.installer.ensure_skills_dir", return_value=target_root),
            patch("skilz.installer.sync_skill_to_configs") as mock_sync,
        ):
            install_local_skill(
                source_path=skill_source,
                agent=None,  # Let detect_agent work
                project_level=True,
                verbose=False,
                force_config=False,
            )

            # Verify: Config sync was NOT called (native support)
            mock_sync.assert_not_called()

        # Verify: Skill installed to .gemini/skills/
        installed_skill = target_root / "test-skill"
        assert installed_skill.exists()
        assert (installed_skill / "SKILL.md").exists()

        # Verify: Manifest created
        manifest = read_manifest(installed_skill)
        assert manifest is not None
        assert manifest.git_repo == "local"  # Local installs use "local" as git_repo

    def test_install_skill_to_gemini_native_user(self, tmp_path, monkeypatch):
        """Install skill to Gemini user-level (~/.gemini/skills/) without config sync."""
        # Setup: Create a fake home directory
        fake_home = tmp_path / "home"
        target_root = fake_home / ".gemini" / "skills"
        target_root.mkdir(parents=True)
        monkeypatch.setattr(Path, "home", lambda: fake_home)

        # Create a test skill source
        skill_source = tmp_path / "user-skill"
        skill_source.mkdir()
        (skill_source / "SKILL.md").write_text("# Test Skill\nA user-level test skill.")

        # Install skill to user-level
        with (
            patch("skilz.installer.detect_agent", return_value="gemini"),
            patch("skilz.installer.ensure_skills_dir", return_value=target_root),
        ):
            install_local_skill(
                source_path=skill_source,
                agent=None,
                project_level=False,
                verbose=False,
                force_config=False,
            )

        # Verify: Skill installed to ~/.gemini/skills/
        installed_skill = target_root / "user-skill"
        assert installed_skill.exists()
        assert (installed_skill / "SKILL.md").exists()

        # Verify: Manifest created
        manifest = read_manifest(installed_skill)
        assert manifest is not None
        assert manifest.git_repo == "local"

    def test_gemini_backward_compat_force_config(self, tmp_path, monkeypatch):
        """Test --force-config flag creates GEMINI.md for backward compatibility."""
        # Setup: Create a Gemini project structure
        project_dir = tmp_path / "project"
        project_dir.mkdir()
        target_root = project_dir / ".gemini" / "skills"
        target_root.mkdir(parents=True)

        # Create a test skill source
        skill_source = tmp_path / "legacy-skill"
        skill_source.mkdir()
        (skill_source / "SKILL.md").write_text("# Legacy Skill\nBackward compat test.")

        # Change to project directory
        monkeypatch.chdir(project_dir)

        # Install skill with force_config=True
        with (
            patch("skilz.installer.detect_agent", return_value="gemini"),
            patch("skilz.installer.ensure_skills_dir", return_value=target_root),
            patch("skilz.installer.sync_skill_to_configs") as mock_sync,
        ):
            install_local_skill(
                source_path=skill_source,
                agent=None,
                project_level=True,
                verbose=False,
                force_config=True,  # Force config sync
            )

            # Verify: Config sync WAS called (backward compat mode)
            mock_sync.assert_called_once()

        # Verify: Skill installed
        installed_skill = target_root / "legacy-skill"
        assert installed_skill.exists()


class TestGeminiAutoDetection:
    """Test Gemini auto-detection scenarios."""

    def test_gemini_auto_detection_project(self, tmp_path, monkeypatch):
        """Auto-detect Gemini from .gemini/ in project directory."""
        # Setup: Create a Gemini project
        project_dir = tmp_path / "project"
        project_dir.mkdir()
        (project_dir / ".gemini").mkdir()

        # Create fake home without Claude
        fake_home = tmp_path / "home"
        fake_home.mkdir()
        monkeypatch.setattr(Path, "home", lambda: fake_home)

        # Detect agent
        agent = detect_agent(project_dir)

        assert agent == "gemini"

    def test_gemini_auto_detection_user(self, tmp_path, monkeypatch):
        """Auto-detect Gemini from ~/.gemini/ in user home."""
        # Setup: Create fake home with Gemini but no Claude
        fake_home = tmp_path / "home"
        (fake_home / ".gemini").mkdir(parents=True)
        monkeypatch.setattr(Path, "home", lambda: fake_home)

        # Empty project directory
        project_dir = tmp_path / "project"
        project_dir.mkdir()

        # Detect agent
        agent = detect_agent(project_dir)

        assert agent == "gemini"

    def test_gemini_priority_over_claude(self, tmp_path, monkeypatch):
        """Ensure Gemini takes priority over Claude when both present (Issue #49 order)."""
        # Setup: Create project with both Claude and Gemini
        project_dir = tmp_path / "project"
        project_dir.mkdir()
        (project_dir / ".claude").mkdir()
        (project_dir / ".gemini").mkdir()

        # Detect agent - Gemini should win (higher popularity in Issue #49)
        agent = detect_agent(project_dir)

        assert agent == "gemini"


class TestGeminiSkillNameValidation:
    """Test skill name validation for Gemini native skills."""

    def test_gemini_invalid_skill_name_warning(self, tmp_path, monkeypatch, capsys):
        """Installing skill with invalid name to Gemini raises an error with helpful suggestion."""
        # Setup: Create a Gemini project
        project_dir = tmp_path / "project"
        project_dir.mkdir()
        target_root = project_dir / ".gemini" / "skills"
        target_root.mkdir(parents=True)

        # Create a skill with invalid name (uppercase + underscore)
        skill_source = tmp_path / "Invalid_Skill"
        skill_source.mkdir()
        (skill_source / "SKILL.md").write_text("# Invalid Skill")

        # Change to project directory
        monkeypatch.chdir(project_dir)

        # Import needed for exception catching
        from skilz.errors import InstallError

        # Install should raise InstallError about invalid name
        with (
            patch("skilz.installer.detect_agent", return_value="gemini"),
            patch("skilz.installer.ensure_skills_dir", return_value=target_root),
            pytest.raises(InstallError, match="invalid-skill"),
        ):
            install_local_skill(
                source_path=skill_source,
                agent=None,
                project_level=True,
                verbose=False,
                force_config=False,
            )

    def test_gemini_valid_skill_name_success(self, tmp_path, monkeypatch):
        """Installing skill with valid name to Gemini succeeds without warnings."""
        # Setup: Create a Gemini project
        project_dir = tmp_path / "project"
        project_dir.mkdir()
        target_root = project_dir / ".gemini" / "skills"
        target_root.mkdir(parents=True)

        # Create a skill with valid name
        skill_source = tmp_path / "valid-skill"
        skill_source.mkdir()
        (skill_source / "SKILL.md").write_text("# Valid Skill")

        # Change to project directory
        monkeypatch.chdir(project_dir)

        # Install should succeed
        with (
            patch("skilz.installer.detect_agent", return_value="gemini"),
            patch("skilz.installer.ensure_skills_dir", return_value=target_root),
        ):
            install_local_skill(
                source_path=skill_source,
                agent=None,
                project_level=True,
                verbose=False,
                force_config=False,
            )

        # Verify installation
        installed_skill = target_root / "valid-skill"
        assert installed_skill.exists()


class TestGeminiConfigSync:
    """Test config sync behavior for Gemini."""

    def test_gemini_skips_config_sync_by_default(self, tmp_path, monkeypatch):
        """Gemini skips config sync by default (native support)."""
        # Setup: Create Gemini project
        project_dir = tmp_path / "project"
        project_dir.mkdir()
        target_root = project_dir / ".gemini" / "skills"
        target_root.mkdir(parents=True)

        # Create a test skill
        skill_source = tmp_path / "test-skill"
        skill_source.mkdir()
        (skill_source / "SKILL.md").write_text("# Test")

        monkeypatch.chdir(project_dir)

        # Install skill
        with (
            patch("skilz.installer.detect_agent", return_value="gemini"),
            patch("skilz.installer.ensure_skills_dir", return_value=target_root),
            patch("skilz.installer.sync_skill_to_configs") as mock_sync,
        ):
            install_local_skill(
                source_path=skill_source,
                agent=None,
                project_level=True,
                verbose=False,
                force_config=False,
            )

            # Verify: sync was not called
            mock_sync.assert_not_called()
