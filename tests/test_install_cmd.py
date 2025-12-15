"""Tests for the install command."""

import argparse
import pytest
from unittest.mock import patch, MagicMock

from skilz.commands.install_cmd import cmd_install
from skilz.errors import SkilzError, SkillNotFoundError, GitError, InstallError


class TestCmdInstall:
    """Tests for cmd_install function."""

    def test_install_success(self):
        """Test successful installation returns 0."""
        args = argparse.Namespace(
            skill_id="test/skill",
            agent=None,
            project=True,
            verbose=False,
        )

        with patch("skilz.installer.install_skill") as mock_install:
            result = cmd_install(args)

        assert result == 0
        mock_install.assert_called_once_with(
            skill_id="test/skill",
            agent=None,
            project_level=True,
            verbose=False,
        )

    def test_install_with_agent(self):
        """Test installation with explicit agent."""
        args = argparse.Namespace(
            skill_id="test/skill",
            agent="opencode",
            project=False,
            verbose=True,
        )

        with patch("skilz.installer.install_skill") as mock_install:
            result = cmd_install(args)

        assert result == 0
        mock_install.assert_called_once_with(
            skill_id="test/skill",
            agent="opencode",
            project_level=False,
            verbose=True,
        )

    def test_install_with_claude_agent(self):
        """Test installation with Claude agent."""
        args = argparse.Namespace(
            skill_id="anthropics/web-artifacts",
            agent="claude",
            project=True,
            verbose=False,
        )

        with patch("skilz.installer.install_skill") as mock_install:
            result = cmd_install(args)

        assert result == 0
        mock_install.assert_called_once_with(
            skill_id="anthropics/web-artifacts",
            agent="claude",
            project_level=True,
            verbose=False,
        )

    def test_install_skill_not_found_error(self, capsys):
        """Test handling of SkillNotFoundError."""
        args = argparse.Namespace(
            skill_id="nonexistent/skill",
            agent=None,
            project=True,
            verbose=False,
        )

        with patch("skilz.installer.install_skill") as mock_install:
            mock_install.side_effect = SkillNotFoundError("nonexistent/skill")
            result = cmd_install(args)

        assert result == 1
        captured = capsys.readouterr()
        assert "Error:" in captured.err
        assert "nonexistent/skill" in captured.err

    def test_install_git_error(self, capsys):
        """Test handling of GitError."""
        args = argparse.Namespace(
            skill_id="test/skill",
            agent=None,
            project=True,
            verbose=False,
        )

        with patch("skilz.installer.install_skill") as mock_install:
            mock_install.side_effect = GitError("clone", "Network error")
            result = cmd_install(args)

        assert result == 1
        captured = capsys.readouterr()
        assert "Error:" in captured.err

    def test_install_install_error(self, capsys):
        """Test handling of InstallError."""
        args = argparse.Namespace(
            skill_id="test/skill",
            agent=None,
            project=True,
            verbose=False,
        )

        with patch("skilz.installer.install_skill") as mock_install:
            mock_install.side_effect = InstallError("test/skill", "Copy failed")
            result = cmd_install(args)

        assert result == 1
        captured = capsys.readouterr()
        assert "Error:" in captured.err

    def test_install_unexpected_error(self, capsys):
        """Test handling of unexpected errors."""
        args = argparse.Namespace(
            skill_id="test/skill",
            agent=None,
            project=True,
            verbose=False,
        )

        with patch("skilz.installer.install_skill") as mock_install:
            mock_install.side_effect = RuntimeError("Unexpected failure")
            result = cmd_install(args)

        assert result == 1
        captured = capsys.readouterr()
        assert "Unexpected error:" in captured.err
        assert "Unexpected failure" in captured.err

    def test_install_missing_verbose_attribute(self):
        """Test handling when verbose attribute is missing."""
        args = argparse.Namespace(
            skill_id="test/skill",
            agent=None,
            project=True,
            # No verbose attribute
        )

        with patch("skilz.installer.install_skill") as mock_install:
            result = cmd_install(args)

        assert result == 0
        # Should default to False for verbose
        mock_install.assert_called_once_with(
            skill_id="test/skill",
            agent=None,
            project_level=True,
            verbose=False,
        )
