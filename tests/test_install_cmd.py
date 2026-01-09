"""Tests for the install command."""

import argparse
from unittest.mock import patch

from skilz.commands.install_cmd import cmd_install, is_git_url
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
            force_config=False,
            config=None,
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
            force_config=False,
            config_file=None,
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
            force_config=False,
            config=None,
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
            force_config=False,
            config_file=None,
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
            force_config=False,
            config=None,
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
            force_config=False,
            config_file=None,
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
            force_config=False,
            config_file=None,
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
            force_config=False,
            config=None,
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
            force_config=False,
            config_file=None,
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
            force_config=False,
            config=None,
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
            force_config=False,
            config_file=None,
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
            force_config=False,
            config=None,
        )

        with patch("skilz.installer.install_local_skill") as mock_install:
            result = cmd_install(args)

        assert result == 0
        mock_install.assert_called_once()
        call_args = mock_install.call_args[1]
        assert str(call_args["source_path"]) == "/path/to/skill"
        assert call_args["project_level"] is True

    def test_install_git_clone_failure(self, capsys):
        """Test that --git option handles clone failures."""
        args = argparse.Namespace(
            skill_id=None,
            agent=None,
            project=False,
            verbose=False,
            file=None,
            git="https://github.com/test/nonexistent-skill.git",
            copy=False,
            symlink=False,
            install_all=False,
            yes_all=False,
        )

        result = cmd_install(args)

        assert result == 1
        captured = capsys.readouterr()
        # Should get a git clone error for non-existent repo
        assert "git clone failed" in captured.err.lower() or "error" in captured.err.lower()


class TestIsGitUrl:
    """Tests for URL auto-detection (SKILZ-48)."""

    def test_https_github_url(self):
        """HTTPS GitHub URLs should be detected."""
        assert is_git_url("https://github.com/owner/repo") is True
        assert is_git_url("https://github.com/anthropics/skills") is True

    def test_http_url(self):
        """HTTP URLs should be detected."""
        assert is_git_url("http://github.com/owner/repo") is True

    def test_ssh_url(self):
        """SSH URLs should be detected."""
        assert is_git_url("git@github.com:owner/repo") is True
        assert is_git_url("git@github.com:owner/repo.git") is True

    def test_dot_git_suffix(self):
        """URLs ending in .git should be detected."""
        assert is_git_url("https://github.com/owner/repo.git") is True
        assert is_git_url("git@gitlab.com:owner/repo.git") is True

    def test_registry_shorthand_not_url(self):
        """Registry shorthand should NOT be detected as URL."""
        assert is_git_url("owner/repo") is False
        assert is_git_url("anthropics_skills/excel") is False

    def test_plain_skill_name_not_url(self):
        """Plain skill names should NOT be detected as URL."""
        assert is_git_url("my-skill") is False
        assert is_git_url("excel") is False

    def test_none_returns_false(self):
        """None input should return False."""
        assert is_git_url(None) is False

    def test_empty_string_returns_false(self):
        """Empty string should return False."""
        assert is_git_url("") is False


class TestUrlAutoDetection:
    """Tests for URL auto-detection in cmd_install (SKILZ-48)."""

    def test_https_url_routes_to_git_install(self, capsys):
        """HTTPS URL in skill_id should route to git installation."""
        args = argparse.Namespace(
            skill_id="https://github.com/owner/skill-repo",
            agent=None,
            project=True,
            verbose=False,
            file=None,
            git=None,  # Not using -g flag
            copy=False,
            symlink=False,
            version_spec=None,
            force_config=False,
            config=None,
            install_all=False,
            yes_all=False,
            skill=None,
        )

        with patch("skilz.git_install.install_from_git") as mock_git_install:
            mock_git_install.return_value = 0
            result = cmd_install(args)

        assert result == 0
        mock_git_install.assert_called_once()
        call_args = mock_git_install.call_args[1]
        assert call_args["git_url"] == "https://github.com/owner/skill-repo"

    def test_ssh_url_routes_to_git_install(self, capsys):
        """SSH URL in skill_id should route to git installation."""
        args = argparse.Namespace(
            skill_id="git@github.com:owner/skill-repo.git",
            agent=None,
            project=True,
            verbose=False,
            file=None,
            git=None,
            copy=False,
            symlink=False,
            version_spec=None,
            force_config=False,
            config=None,
            install_all=False,
            yes_all=False,
            skill=None,
        )

        with patch("skilz.git_install.install_from_git") as mock_git_install:
            mock_git_install.return_value = 0
            result = cmd_install(args)

        assert result == 0
        mock_git_install.assert_called_once()
        call_args = mock_git_install.call_args[1]
        assert call_args["git_url"] == "git@github.com:owner/skill-repo.git"

    def test_explicit_git_flag_takes_precedence(self):
        """Explicit -g flag should take precedence over URL detection."""
        args = argparse.Namespace(
            skill_id=None,
            agent=None,
            project=True,
            verbose=False,
            file=None,
            git="https://github.com/explicit/repo",  # Using -g flag
            copy=False,
            symlink=False,
            version_spec=None,
            force_config=False,
            config=None,
            install_all=False,
            yes_all=False,
            skill=None,
        )

        with patch("skilz.git_install.install_from_git") as mock_git_install:
            mock_git_install.return_value = 0
            result = cmd_install(args)

        assert result == 0
        mock_git_install.assert_called_once()
        call_args = mock_git_install.call_args[1]
        assert call_args["git_url"] == "https://github.com/explicit/repo"

    def test_registry_id_still_works(self):
        """Registry skill IDs should still route to registry install."""
        args = argparse.Namespace(
            skill_id="anthropics/excel",
            agent=None,
            project=True,
            verbose=False,
            file=None,
            git=None,
            copy=False,
            symlink=False,
            version_spec=None,
            force_config=False,
            config=None,
        )

        with patch("skilz.installer.install_skill") as mock_install:
            result = cmd_install(args)

        assert result == 0
        mock_install.assert_called_once()
        call_args = mock_install.call_args[1]
        assert call_args["skill_id"] == "anthropics/excel"

    def test_config_flag_requires_project(self, capsys):
        """--config flag requires --project flag (SKILZ-50)."""
        args = argparse.Namespace(
            skill_id="test/skill",
            agent="universal",
            project=False,  # Missing --project
            config="GEMINI.md",  # But has --config
            verbose=False,
            file=None,
            git=None,
            copy=False,
            symlink=False,
            version_spec=None,
            force_config=False,
        )

        result = cmd_install(args)

        assert result == 1  # Should fail
        captured = capsys.readouterr()
        assert "--config requires --project" in captured.err

    def test_config_flag_with_project(self):
        """--config flag works when --project is provided (SKILZ-50)."""
        args = argparse.Namespace(
            skill_id="test/skill",
            agent="universal",
            project=True,  # Has --project
            config="GEMINI.md",  # And --config
            verbose=False,
            file=None,
            git=None,
            copy=False,
            symlink=False,
            version_spec=None,
            force_config=False,
        )

        with patch("skilz.installer.install_skill") as mock_install:
            result = cmd_install(args)

        # Should succeed (validation passes)
        assert result == 0
        mock_install.assert_called_once()
