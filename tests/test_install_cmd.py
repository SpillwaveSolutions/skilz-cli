"""Tests for the install command."""

import argparse
from unittest.mock import patch

from skilz.commands.install_cmd import cmd_install
from skilz.errors import GitError, InstallError, SkillNotFoundError


class TestCmdInstall:
    """Tests for cmd_install function."""

    def test_install_success(self):
        """Test successful installation returns 0."""
        args = argparse.Namespace(
            skill_id="test/skill",
            agent=None,
            project=True,
            verbose=False,
            file=None,
            git=None,
            copy=False,
            symlink=False,
            version_spec=None,
        )

        with patch("skilz.installer.install_skill") as mock_install:
            result = cmd_install(args)

        assert result == 0
        mock_install.assert_called_once_with(
            skill_id="test/skill",
            agent=None,
            project_level=True,
            verbose=False,
            mode=None,
            version_spec=None,
        )

    def test_install_with_agent(self):
        """Test installation with explicit agent."""
        args = argparse.Namespace(
            skill_id="test/skill",
            agent="opencode",
            project=False,
            verbose=True,
            file=None,
            git=None,
            copy=False,
            symlink=False,
            version_spec=None,
        )

        with patch("skilz.installer.install_skill") as mock_install:
            result = cmd_install(args)

        assert result == 0
        mock_install.assert_called_once_with(
            skill_id="test/skill",
            agent="opencode",
            project_level=False,
            verbose=True,
            mode=None,
            version_spec=None,
        )

    def test_install_with_claude_agent(self):
        """Test installation with Claude agent."""
        args = argparse.Namespace(
            skill_id="anthropics/web-artifacts",
            agent="claude",
            project=True,
            verbose=False,
            file=None,
            git=None,
            copy=False,
            symlink=False,
            version_spec=None,
        )

        with patch("skilz.installer.install_skill") as mock_install:
            result = cmd_install(args)

        assert result == 0
        mock_install.assert_called_once_with(
            skill_id="anthropics/web-artifacts",
            agent="claude",
            project_level=True,
            verbose=False,
            mode=None,
            version_spec=None,
        )

    def test_install_skill_not_found_error(self, capsys):
        """Test handling of SkillNotFoundError."""
        args = argparse.Namespace(
            skill_id="nonexistent/skill",
            agent=None,
            project=True,
            verbose=False,
            file=None,
            git=None,
            copy=False,
            symlink=False,
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
            file=None,
            git=None,
            copy=False,
            symlink=False,
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
            file=None,
            git=None,
            copy=False,
            symlink=False,
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
            file=None,
            git=None,
            copy=False,
            symlink=False,
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
            file=None,
            git=None,
            copy=False,
            symlink=False,
            # No verbose attribute - version_spec also omitted
        )

        with patch("skilz.installer.install_skill") as mock_install:
            result = cmd_install(args)

        assert result == 0
        # Should default to False for verbose and None for version_spec
        mock_install.assert_called_once_with(
            skill_id="test/skill",
            agent=None,
            project_level=True,
            verbose=False,
            mode=None,
            version_spec=None,
        )

    def test_install_with_copy_flag(self):
        """Test installation with --copy flag passes mode='copy'."""
        args = argparse.Namespace(
            skill_id="test/skill",
            agent=None,
            project=False,
            verbose=False,
            file=None,
            git=None,
            copy=True,
            symlink=False,
            version_spec=None,
        )

        with patch("skilz.installer.install_skill") as mock_install:
            result = cmd_install(args)

        assert result == 0
        mock_install.assert_called_once_with(
            skill_id="test/skill",
            agent=None,
            project_level=False,
            verbose=False,
            mode="copy",
            version_spec=None,
        )

    def test_install_with_symlink_flag(self):
        """Test installation with --symlink flag passes mode='symlink'."""
        args = argparse.Namespace(
            skill_id="test/skill",
            agent=None,
            project=False,
            verbose=False,
            file=None,
            git=None,
            copy=False,
            symlink=True,
            version_spec=None,
        )

        with patch("skilz.installer.install_skill") as mock_install:
            result = cmd_install(args)

        assert result == 0
        mock_install.assert_called_once_with(
            skill_id="test/skill",
            agent=None,
            project_level=False,
            verbose=False,
            mode="symlink",
            version_spec=None,
        )

    def test_install_no_source_error(self, capsys):
        """Test error when no source is specified."""
        args = argparse.Namespace(
            skill_id=None,
            agent=None,
            project=False,
            verbose=False,
            file=None,
            git=None,
            copy=False,
            symlink=False,
        )

        result = cmd_install(args)

        assert result == 1
        captured = capsys.readouterr()
        assert "Error:" in captured.err
        assert "skill_id" in captured.err or "file" in captured.err or "git" in captured.err

    def test_install_multiple_sources_error(self, capsys):
        """Test error when multiple sources are specified."""
        args = argparse.Namespace(
            skill_id="test/skill",
            agent=None,
            project=False,
            verbose=False,
            file="/path/to/skill",
            git=None,
            copy=False,
            symlink=False,
        )

        result = cmd_install(args)

        assert result == 1
        captured = capsys.readouterr()
        assert "Error:" in captured.err

    def test_install_from_file_success(self):
        """Test successful installation from local file."""
        args = argparse.Namespace(
            skill_id=None,
            agent=None,
            project=True,
            verbose=False,
            file="/path/to/skill",
            git=None,
            copy=False,
            symlink=False,
            version_spec=None,
        )

        with patch("skilz.installer.install_local_skill") as mock_install:
            result = cmd_install(args)

        assert result == 0
        mock_install.assert_called_once()
        call_args = mock_install.call_args[1]
        assert str(call_args["source_path"]) == "/path/to/skill"
        assert call_args["project_level"] is True

    def test_install_git_not_implemented(self, capsys):
        """Test that --git option returns not implemented error."""
        args = argparse.Namespace(
            skill_id=None,
            agent=None,
            project=False,
            verbose=False,
            file=None,
            git="https://github.com/test/skill.git",
            copy=False,
            symlink=False,
        )

        result = cmd_install(args)

        assert result == 1
        captured = capsys.readouterr()
        assert "not yet implemented" in captured.err.lower()
