"""Tests for the remove command."""

import argparse
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
