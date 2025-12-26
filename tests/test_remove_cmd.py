"""Tests for the remove command."""

import argparse
from pathlib import Path
from unittest.mock import patch

import pytest

from skilz.commands.remove_cmd import cmd_remove, confirm_remove
from skilz.manifest import SkillManifest, write_manifest
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
def installed_skill_with_dir(temp_dir, sample_manifest):
    """Create an installed skill with actual directory."""
    skill_dir = temp_dir / "plantuml"
    skill_dir.mkdir(parents=True)
    (skill_dir / "SKILL.md").write_text("# Test Skill")
    write_manifest(skill_dir, sample_manifest)

    return InstalledSkill(
        skill_id="spillwave/plantuml",
        skill_name="plantuml",
        path=skill_dir,
        manifest=sample_manifest,
        agent="claude",
        project_level=True,
        install_mode="copy",
    )


class TestConfirmRemove:
    """Tests for confirm_remove function."""

    def test_confirm_yes(self):
        """Test confirmation with 'y' input."""
        with patch("builtins.input", return_value="y"):
            result = confirm_remove("test/skill", "Claude Code")
        assert result is True

    def test_confirm_yes_full(self):
        """Test confirmation with 'yes' input."""
        with patch("builtins.input", return_value="yes"):
            result = confirm_remove("test/skill", "Claude Code")
        assert result is True

    def test_confirm_no(self):
        """Test confirmation with 'n' input."""
        with patch("builtins.input", return_value="n"):
            result = confirm_remove("test/skill", "Claude Code")
        assert result is False

    def test_confirm_empty(self):
        """Test confirmation with empty input (default no)."""
        with patch("builtins.input", return_value=""):
            result = confirm_remove("test/skill", "Claude Code")
        assert result is False

    def test_confirm_keyboard_interrupt(self):
        """Test confirmation with keyboard interrupt."""
        with patch("builtins.input", side_effect=KeyboardInterrupt):
            result = confirm_remove("test/skill", "Claude Code")
        assert result is False


class TestCmdRemove:
    """Tests for cmd_remove function."""

    def test_remove_skill_not_found(self, capsys):
        """Test removing a skill that doesn't exist."""
        args = argparse.Namespace(
            skill_id="nonexistent/skill",
            agent="claude",
            project=True,
            yes=True,
            verbose=False,
        )

        with patch("skilz.commands.remove_cmd.find_installed_skill") as mock_find:
            mock_find.return_value = None
            result = cmd_remove(args)

        assert result == 1
        captured = capsys.readouterr()
        assert "not found" in captured.err.lower()

    def test_remove_with_confirmation(self, installed_skill_with_dir, capsys):
        """Test removing a skill with confirmation."""
        args = argparse.Namespace(
            skill_id="spillwave/plantuml",
            agent="claude",
            project=True,
            yes=False,
            verbose=False,
        )

        with patch("skilz.commands.remove_cmd.find_installed_skill") as mock_find:
            mock_find.return_value = installed_skill_with_dir

            with patch("skilz.commands.remove_cmd.confirm_remove", return_value=True):
                result = cmd_remove(args)

        assert result == 0
        captured = capsys.readouterr()
        assert "Removed:" in captured.out
        # Directory should be deleted
        assert not installed_skill_with_dir.path.exists()

    def test_remove_cancelled(self, installed_skill_with_dir, capsys):
        """Test removing a skill with cancelled confirmation."""
        args = argparse.Namespace(
            skill_id="spillwave/plantuml",
            agent="claude",
            project=True,
            yes=False,
            verbose=False,
        )

        with patch("skilz.commands.remove_cmd.find_installed_skill") as mock_find:
            mock_find.return_value = installed_skill_with_dir

            with patch("skilz.commands.remove_cmd.confirm_remove", return_value=False):
                result = cmd_remove(args)

        assert result == 0
        captured = capsys.readouterr()
        assert "Cancelled" in captured.out
        # Directory should still exist
        assert installed_skill_with_dir.path.exists()

    def test_remove_with_yes_flag(self, installed_skill_with_dir, capsys):
        """Test removing a skill with --yes flag (no confirmation)."""
        args = argparse.Namespace(
            skill_id="spillwave/plantuml",
            agent="claude",
            project=True,
            yes=True,
            verbose=False,
        )

        with patch("skilz.commands.remove_cmd.find_installed_skill") as mock_find:
            mock_find.return_value = installed_skill_with_dir
            result = cmd_remove(args)

        assert result == 0
        captured = capsys.readouterr()
        assert "Removed:" in captured.out
        # Directory should be deleted
        assert not installed_skill_with_dir.path.exists()

    def test_remove_verbose(self, installed_skill_with_dir, capsys):
        """Test removing a skill with verbose output."""
        args = argparse.Namespace(
            skill_id="spillwave/plantuml",
            agent="claude",
            project=True,
            yes=True,
            verbose=True,
        )

        with patch("skilz.commands.remove_cmd.find_installed_skill") as mock_find:
            mock_find.return_value = installed_skill_with_dir
            result = cmd_remove(args)

        assert result == 0
        captured = capsys.readouterr()
        assert "Removing" in captured.out

    def test_remove_by_name(self, installed_skill_with_dir, capsys):
        """Test removing a skill by name instead of full ID."""
        args = argparse.Namespace(
            skill_id="plantuml",  # Just the name, not full ID
            agent="claude",
            project=True,
            yes=True,
            verbose=False,
        )

        with patch("skilz.commands.remove_cmd.find_installed_skill") as mock_find:
            mock_find.return_value = installed_skill_with_dir
            result = cmd_remove(args)

        assert result == 0
        # find_installed_skill should be called with the name
        mock_find.assert_called_once_with(
            "plantuml",
            agent="claude",
            project_level=True,
        )

    def test_remove_with_global_yes_all_flag(self, installed_skill_with_dir, capsys):
        """Test removing a skill with global -y/--yes-all flag."""
        args = argparse.Namespace(
            skill_id="spillwave/plantuml",
            agent="claude",
            project=True,
            yes=False,  # Command-level flag is False
            yes_all=True,  # But global flag is True
            verbose=False,
        )

        with patch("skilz.commands.remove_cmd.find_installed_skill") as mock_find:
            mock_find.return_value = installed_skill_with_dir

            # confirm_remove should NOT be called because yes_all is True
            with patch("skilz.commands.remove_cmd.confirm_remove") as mock_confirm:
                result = cmd_remove(args)
                mock_confirm.assert_not_called()

        assert result == 0
        captured = capsys.readouterr()
        assert "Removed:" in captured.out
        # Directory should be deleted
        assert not installed_skill_with_dir.path.exists()

    def test_remove_without_yes_all_attribute(self, installed_skill_with_dir, capsys):
        """Test removing works when yes_all attribute is missing (backwards compat)."""
        args = argparse.Namespace(
            skill_id="spillwave/plantuml",
            agent="claude",
            project=True,
            yes=True,
            verbose=False,
            # Note: no yes_all attribute - should use getattr default
        )

        with patch("skilz.commands.remove_cmd.find_installed_skill") as mock_find:
            mock_find.return_value = installed_skill_with_dir
            result = cmd_remove(args)

        assert result == 0
        captured = capsys.readouterr()
        assert "Removed:" in captured.out


class TestSymlinkRemoval:
    """Tests for symlink-related removal functionality."""

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
        (skill_dir / "SKILL.md").write_text("# Test Skill")
        write_manifest(skill_dir, symlink_manifest)

        return InstalledSkill(
            skill_id="spillwave/plantuml",
            skill_name="plantuml",
            path=skill_dir,
            manifest=symlink_manifest,
            agent="claude",
            project_level=True,
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
        write_manifest(skill_dir, manifest)

        return InstalledSkill(
            skill_id="spillwave/broken",
            skill_name="broken",
            path=skill_dir,
            manifest=manifest,
            agent="claude",
            project_level=True,
            install_mode="symlink",
            canonical_path=Path("/nonexistent/path"),
            is_broken=True,
        )

    def test_remove_symlink_with_yes_flag(self, symlinked_skill, capsys):
        """Test removing a symlinked skill with --yes flag."""
        args = argparse.Namespace(
            skill_id="spillwave/plantuml",
            agent="claude",
            project=True,
            yes=True,
            verbose=False,
        )

        with patch("skilz.commands.remove_cmd.find_installed_skill") as mock_find:
            mock_find.return_value = symlinked_skill
            result = cmd_remove(args)

        assert result == 0
        captured = capsys.readouterr()
        assert "Removed symlink:" in captured.out
        assert not symlinked_skill.path.exists()

    def test_remove_symlink_shows_verbose_mode(self, symlinked_skill, capsys):
        """Test verbose output shows symlink mode."""
        args = argparse.Namespace(
            skill_id="spillwave/plantuml",
            agent="claude",
            project=True,
            yes=True,
            verbose=True,
        )

        with patch("skilz.commands.remove_cmd.find_installed_skill") as mock_find:
            mock_find.return_value = symlinked_skill
            result = cmd_remove(args)

        assert result == 0
        captured = capsys.readouterr()
        assert "mode: symlink" in captured.out

    def test_remove_symlink_confirmation_message(self, symlinked_skill, capsys):
        """Test symlink removal shows different confirmation message."""
        args = argparse.Namespace(
            skill_id="spillwave/plantuml",
            agent="claude",
            project=True,
            yes=False,
            verbose=False,
        )

        with patch("skilz.commands.remove_cmd.find_installed_skill") as mock_find:
            mock_find.return_value = symlinked_skill

            # Mock user declining to confirm
            with patch("builtins.input", return_value="n"):
                result = cmd_remove(args)

        assert result == 0
        captured = capsys.readouterr()
        assert "Cancelled" in captured.out
        # Skill should still exist since user cancelled
        assert symlinked_skill.path.exists()

    def test_remove_symlink_confirms_with_canonical_path(self, symlinked_skill, capsys):
        """Test symlink confirmation mentions canonical path will be preserved."""
        args = argparse.Namespace(
            skill_id="spillwave/plantuml",
            agent="claude",
            project=True,
            yes=False,
            verbose=False,
        )

        captured_prompt = None

        def capture_input(prompt):
            nonlocal captured_prompt
            captured_prompt = prompt
            return "y"

        with patch("skilz.commands.remove_cmd.find_installed_skill") as mock_find:
            mock_find.return_value = symlinked_skill
            with patch("builtins.input", side_effect=capture_input):
                result = cmd_remove(args)

        assert result == 0
        # Check that the prompt mentioned canonical path being preserved
        assert "preserved" in captured_prompt

    def test_remove_broken_symlink(self, broken_symlink_skill, capsys):
        """Test removing a broken symlink skill."""
        args = argparse.Namespace(
            skill_id="spillwave/broken",
            agent="claude",
            project=True,
            yes=True,
            verbose=True,
        )

        with patch("skilz.commands.remove_cmd.find_installed_skill") as mock_find:
            mock_find.return_value = broken_symlink_skill
            result = cmd_remove(args)

        assert result == 0
        captured = capsys.readouterr()
        assert "broken symlink" in captured.out.lower()
        assert not broken_symlink_skill.path.exists()

    def test_remove_copy_shows_removed_not_symlink(self, installed_skill_with_dir, capsys):
        """Test removing a copied skill shows 'Removed:' not 'Removed symlink:'."""
        args = argparse.Namespace(
            skill_id="spillwave/plantuml",
            agent="claude",
            project=True,
            yes=True,
            verbose=False,
        )

        with patch("skilz.commands.remove_cmd.find_installed_skill") as mock_find:
            mock_find.return_value = installed_skill_with_dir
            result = cmd_remove(args)

        assert result == 0
        captured = capsys.readouterr()
        assert "Removed:" in captured.out
        assert "Removed symlink:" not in captured.out
