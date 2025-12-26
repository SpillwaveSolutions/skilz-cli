"""Tests for the update command."""

import argparse
from pathlib import Path
from unittest.mock import patch

import pytest

from skilz.commands.update_cmd import check_skill_update, cmd_update
from skilz.manifest import SkillManifest
from skilz.registry import SkillInfo
from skilz.scanner import InstalledSkill


@pytest.fixture
def sample_manifest():
    """Create a sample manifest."""
    return SkillManifest.create(
        skill_id="spillwave/plantuml",
        git_repo="https://github.com/SpillwaveSolutions/plantuml.git",
        skill_path="/main/SKILL.md",
        git_sha="f2489dcd47799e4aaff3ae0a34cde0ebf2288a66",
    )


@pytest.fixture
def sample_installed_skill(temp_dir, sample_manifest):
    """Create a sample installed skill."""
    skill_dir = temp_dir / "plantuml"
    skill_dir.mkdir(parents=True)
    return InstalledSkill(
        skill_id="spillwave/plantuml",
        skill_name="plantuml",
        path=skill_dir,
        manifest=sample_manifest,
        agent="claude",
        project_level=False,
        install_mode="copy",
    )


class TestCheckSkillUpdate:
    """Tests for check_skill_update function."""

    def test_no_update_needed(self, sample_installed_skill):
        """Test when skill is up-to-date."""
        with patch("skilz.commands.update_cmd.lookup_skill") as mock_lookup:
            mock_lookup.return_value = SkillInfo(
                skill_id="spillwave/plantuml",
                git_repo="https://github.com/SpillwaveSolutions/plantuml.git",
                skill_path="/main/SKILL.md",
                git_sha="f2489dcd47799e4aaff3ae0a34cde0ebf2288a66",  # Same SHA
            )

            needs_update, new_sha = check_skill_update(sample_installed_skill)

            assert needs_update is False
            assert new_sha is None

    def test_update_needed(self, sample_installed_skill):
        """Test when skill needs update."""
        with patch("skilz.commands.update_cmd.lookup_skill") as mock_lookup:
            mock_lookup.return_value = SkillInfo(
                skill_id="spillwave/plantuml",
                git_repo="https://github.com/SpillwaveSolutions/plantuml.git",
                skill_path="/main/SKILL.md",
                git_sha="new_sha_from_registry_1234567890abcdef",  # Different SHA
            )

            needs_update, new_sha = check_skill_update(sample_installed_skill)

            assert needs_update is True
            assert new_sha == "new_sha_from_registry_1234567890abcdef"

    def test_not_in_registry(self, sample_installed_skill):
        """Test when skill not found in registry."""
        with patch("skilz.commands.update_cmd.lookup_skill") as mock_lookup:
            mock_lookup.side_effect = Exception("Skill not found")

            needs_update, new_sha = check_skill_update(sample_installed_skill)

            assert needs_update is False
            assert new_sha is None


class TestCmdUpdate:
    """Tests for cmd_update function."""

    def test_update_no_skills_installed(self, capsys):
        """Test update when no skills are installed."""
        args = argparse.Namespace(
            skill_id=None,
            agent="claude",
            project=True,
            dry_run=False,
            verbose=False,
        )

        with patch("skilz.commands.update_cmd.scan_installed_skills") as mock_scan:
            mock_scan.return_value = []
            result = cmd_update(args)

        assert result == 0
        captured = capsys.readouterr()
        assert "No skills installed" in captured.out

    def test_update_all_up_to_date(self, sample_installed_skill, capsys):
        """Test update when all skills are up-to-date."""
        args = argparse.Namespace(
            skill_id=None,
            agent="claude",
            project=True,
            dry_run=False,
            verbose=False,
        )

        with patch("skilz.commands.update_cmd.scan_installed_skills") as mock_scan:
            mock_scan.return_value = [sample_installed_skill]

            with patch("skilz.commands.update_cmd.check_skill_update") as mock_check:
                mock_check.return_value = (False, None)

                with patch("skilz.commands.update_cmd.lookup_skill") as mock_lookup:
                    # Indicate skill is in registry (up-to-date, not unknown)
                    mock_lookup.return_value = SkillInfo(
                        skill_id="spillwave/plantuml",
                        git_repo="test",
                        skill_path="/test",
                        git_sha="test",
                    )

                    result = cmd_update(args)

        assert result == 0
        captured = capsys.readouterr()
        assert "up-to-date" in captured.out

    def test_update_dry_run(self, sample_installed_skill, capsys):
        """Test update with dry-run flag."""
        args = argparse.Namespace(
            skill_id=None,
            agent="claude",
            project=True,
            dry_run=True,
            verbose=False,
        )

        with patch("skilz.commands.update_cmd.scan_installed_skills") as mock_scan:
            mock_scan.return_value = [sample_installed_skill]

            with patch("skilz.commands.update_cmd.check_skill_update") as mock_check:
                mock_check.return_value = (True, "new_sha_1234567890abcdef")

                with patch("skilz.commands.update_cmd.install_skill") as mock_install:
                    result = cmd_update(args)

                    # Should NOT call install_skill in dry-run mode
                    mock_install.assert_not_called()

        assert result == 0
        captured = capsys.readouterr()
        assert "would update" in captured.out.lower()

    def test_update_specific_skill(self, sample_installed_skill, capsys):
        """Test updating a specific skill by ID."""
        args = argparse.Namespace(
            skill_id="spillwave/plantuml",
            agent="claude",
            project=True,
            dry_run=True,
            verbose=False,
        )

        with patch("skilz.commands.update_cmd.find_installed_skill") as mock_find:
            mock_find.return_value = sample_installed_skill

            with patch("skilz.commands.update_cmd.check_skill_update") as mock_check:
                mock_check.return_value = (True, "new_sha_1234567890abcdef")

                result = cmd_update(args)

        assert result == 0
        captured = capsys.readouterr()
        assert "spillwave/plantuml" in captured.out

    def test_update_specific_skill_not_found(self, capsys):
        """Test updating a skill that doesn't exist."""
        args = argparse.Namespace(
            skill_id="nonexistent/skill",
            agent="claude",
            project=True,
            dry_run=False,
            verbose=False,
        )

        with patch("skilz.commands.update_cmd.find_installed_skill") as mock_find:
            mock_find.return_value = None
            result = cmd_update(args)

        assert result == 1
        captured = capsys.readouterr()
        assert "not found" in captured.err.lower()

    def test_update_performs_install(self, sample_installed_skill, capsys):
        """Test that update calls install_skill for outdated skills."""
        args = argparse.Namespace(
            skill_id=None,
            agent="claude",
            project=True,
            dry_run=False,
            verbose=False,
        )

        with patch("skilz.commands.update_cmd.scan_installed_skills") as mock_scan:
            mock_scan.return_value = [sample_installed_skill]

            with patch("skilz.commands.update_cmd.check_skill_update") as mock_check:
                mock_check.return_value = (True, "new_sha_1234567890abcdef")

                with patch("skilz.commands.update_cmd.install_skill") as mock_install:
                    result = cmd_update(args)

                    # Should call install_skill with mode
                    mock_install.assert_called_once_with(
                        skill_id="spillwave/plantuml",
                        agent="claude",
                        project_level=False,
                        verbose=False,
                        mode="copy",
                    )

        assert result == 0
        captured = capsys.readouterr()
        assert "updating" in captured.out.lower()


class TestSymlinkUpdate:
    """Tests for symlink-related update functionality."""

    @pytest.fixture
    def symlink_manifest(self):
        """Create a manifest for a symlinked skill."""
        return SkillManifest.create(
            skill_id="spillwave/plantuml",
            git_repo="https://github.com/SpillwaveSolutions/plantuml.git",
            skill_path="/main/SKILL.md",
            git_sha="f2489dcd47799e4aaff3ae0a34cde0ebf2288a66",
            install_mode="symlink",
            canonical_path="/home/user/.skilz/skills/plantuml",
        )

    @pytest.fixture
    def symlinked_skill(self, temp_dir, symlink_manifest):
        """Create a symlinked skill."""
        skill_dir = temp_dir / "plantuml"
        skill_dir.mkdir(parents=True)
        return InstalledSkill(
            skill_id="spillwave/plantuml",
            skill_name="plantuml",
            path=skill_dir,
            manifest=symlink_manifest,
            agent="claude",
            project_level=False,
            install_mode="symlink",
            canonical_path=Path("/home/user/.skilz/skills/plantuml"),
        )

    @pytest.fixture
    def broken_symlink_skill(self, temp_dir):
        """Create a broken symlink skill."""
        manifest = SkillManifest.create(
            skill_id="spillwave/broken",
            git_repo="https://github.com/SpillwaveSolutions/broken.git",
            skill_path="/main/SKILL.md",
            git_sha="abc123",
            install_mode="symlink",
            canonical_path="/nonexistent/path",
        )
        skill_dir = temp_dir / "broken"
        skill_dir.mkdir(parents=True)
        return InstalledSkill(
            skill_id="spillwave/broken",
            skill_name="broken",
            path=skill_dir,
            manifest=manifest,
            agent="claude",
            project_level=False,
            install_mode="symlink",
            canonical_path=Path("/nonexistent/path"),
            is_broken=True,
        )

    def test_update_symlink_passes_mode(self, symlinked_skill, capsys):
        """Test that update passes mode='symlink' for symlinked skills."""
        args = argparse.Namespace(
            skill_id=None,
            agent="claude",
            project=True,
            dry_run=False,
            verbose=False,
        )

        with patch("skilz.commands.update_cmd.scan_installed_skills") as mock_scan:
            mock_scan.return_value = [symlinked_skill]

            with patch("skilz.commands.update_cmd.check_skill_update") as mock_check:
                mock_check.return_value = (True, "new_sha_1234567890abcdef")

                with patch("skilz.commands.update_cmd.install_skill") as mock_install:
                    result = cmd_update(args)

                    mock_install.assert_called_once_with(
                        skill_id="spillwave/plantuml",
                        agent="claude",
                        project_level=False,
                        verbose=False,
                        mode="symlink",
                    )

        assert result == 0

    def test_update_shows_mode_in_verbose(self, symlinked_skill, capsys):
        """Test that verbose output shows symlink mode."""
        args = argparse.Namespace(
            skill_id=None,
            agent="claude",
            project=True,
            dry_run=True,
            verbose=True,
        )

        with patch("skilz.commands.update_cmd.scan_installed_skills") as mock_scan:
            mock_scan.return_value = [symlinked_skill]

            with patch("skilz.commands.update_cmd.check_skill_update") as mock_check:
                mock_check.return_value = (True, "new_sha_1234567890abcdef")

                result = cmd_update(args)

        assert result == 0
        captured = capsys.readouterr()
        assert "[symlink]" in captured.out

    def test_update_broken_symlink_skipped(self, broken_symlink_skill, capsys):
        """Test that broken symlinks are skipped and reported."""
        args = argparse.Namespace(
            skill_id=None,
            agent="claude",
            project=True,
            dry_run=False,
            verbose=False,
        )

        with patch("skilz.commands.update_cmd.scan_installed_skills") as mock_scan:
            mock_scan.return_value = [broken_symlink_skill]

            with patch("skilz.commands.update_cmd.install_skill") as mock_install:
                result = cmd_update(args)

                # Should NOT call install_skill for broken symlinks
                mock_install.assert_not_called()

        assert result == 0
        captured = capsys.readouterr()
        assert "broken symlink" in captured.out.lower()
        assert "1 broken" in captured.out

    def test_update_summary_shows_broken_count(self, broken_symlink_skill, capsys):
        """Test that summary includes broken symlink count."""
        args = argparse.Namespace(
            skill_id=None,
            agent="claude",
            project=True,
            dry_run=False,
            verbose=False,
        )

        with patch("skilz.commands.update_cmd.scan_installed_skills") as mock_scan:
            mock_scan.return_value = [broken_symlink_skill]
            result = cmd_update(args)

        assert result == 0
        captured = capsys.readouterr()
        assert "broken" in captured.out

    def test_update_copy_shows_mode_in_verbose(self, sample_installed_skill, capsys):
        """Test that verbose output shows copy mode for copied skills."""
        args = argparse.Namespace(
            skill_id=None,
            agent="claude",
            project=True,
            dry_run=True,
            verbose=True,
        )

        with patch("skilz.commands.update_cmd.scan_installed_skills") as mock_scan:
            mock_scan.return_value = [sample_installed_skill]

            with patch("skilz.commands.update_cmd.check_skill_update") as mock_check:
                mock_check.return_value = (True, "new_sha_1234567890abcdef")

                result = cmd_update(args)

        assert result == 0
        captured = capsys.readouterr()
        assert "[copy]" in captured.out
