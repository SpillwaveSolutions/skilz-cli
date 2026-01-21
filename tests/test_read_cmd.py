"""Tests for read command."""

import argparse
from pathlib import Path
from unittest.mock import patch

import pytest

from skilz.commands.read_cmd import cmd_read
from skilz.manifest import SkillManifest
from skilz.scanner import InstalledSkill


@pytest.fixture
def mock_skill(tmp_path: Path) -> InstalledSkill:
    """Create a mock installed skill with SKILL.md."""
    skill_dir = tmp_path / "skills" / "test-skill"
    skill_dir.mkdir(parents=True, exist_ok=True)

    # Create SKILL.md
    skill_md = skill_dir / "SKILL.md"
    skill_md.write_text("""---
name: test-skill
description: A test skill for testing
---
# Test Skill

This is a test skill that does testing things.

## Usage

Use it for testing.
""")

    manifest = SkillManifest(
        installed_at="2025-01-15T12:00:00Z",
        skill_id="owner/test-skill",
        git_repo="https://github.com/owner/repo",
        skill_path="skills/test-skill",
        git_sha="abc123def456",
        skilz_version="1.0.0",
        install_mode="copy",
    )

    return InstalledSkill(
        skill_id="owner/test-skill",
        skill_name="test-skill",
        path=skill_dir,
        manifest=manifest,
        agent="claude",
        project_level=False,
        install_mode="copy",
    )


@pytest.fixture
def mock_broken_skill(tmp_path: Path) -> InstalledSkill:
    """Create a mock broken symlink skill."""
    manifest = SkillManifest(
        installed_at="unknown",
        skill_id="unknown/broken-skill",
        git_repo="unknown",
        skill_path="unknown",
        git_sha="unknown",
        skilz_version="unknown",
        install_mode="symlink",
    )

    return InstalledSkill(
        skill_id="unknown/broken-skill",
        skill_name="broken-skill",
        path=tmp_path / "broken-skill",
        manifest=manifest,
        agent="claude",
        project_level=False,
        install_mode="symlink",
        canonical_path=Path("/nonexistent/path"),
        is_broken=True,
    )


class TestReadCommand:
    """Tests for cmd_read function."""

    def test_read_existing_skill(
        self, mock_skill: InstalledSkill, capsys: pytest.CaptureFixture
    ) -> None:
        """Test reading an existing skill."""
        args = argparse.Namespace(
            skill_name="test-skill",
            agent=None,
            project=False,
        )

        with patch("skilz.commands.read_cmd.find_installed_skill") as mock_find:
            mock_find.return_value = mock_skill

            result = cmd_read(args)

            assert result == 0

            captured = capsys.readouterr()
            assert "# Skill: test-skill" in captured.out
            assert "# Base Directory:" in captured.out
            assert "# SKILL.md Path:" in captured.out
            assert "This is a test skill" in captured.out

    def test_read_skill_not_found(self, capsys: pytest.CaptureFixture) -> None:
        """Test error when skill is not found."""
        args = argparse.Namespace(
            skill_name="nonexistent-skill",
            agent=None,
            project=False,
        )

        with patch("skilz.commands.read_cmd.find_installed_skill") as mock_find:
            mock_find.return_value = None

            result = cmd_read(args)

            assert result == 1

            captured = capsys.readouterr()
            assert "Error: Skill 'nonexistent-skill' not found" in captured.err

    def test_read_broken_symlink(
        self, mock_broken_skill: InstalledSkill, capsys: pytest.CaptureFixture
    ) -> None:
        """Test error when skill has broken symlink."""
        args = argparse.Namespace(
            skill_name="broken-skill",
            agent=None,
            project=False,
        )

        with patch("skilz.commands.read_cmd.find_installed_skill") as mock_find:
            mock_find.return_value = mock_broken_skill

            result = cmd_read(args)

            assert result == 1

            captured = capsys.readouterr()
            assert "broken symlink" in captured.err

    def test_read_skill_missing_skill_md(
        self, tmp_path: Path, capsys: pytest.CaptureFixture
    ) -> None:
        """Test error when SKILL.md is missing."""
        # Create skill without SKILL.md
        skill_dir = tmp_path / "skills" / "no-skillmd"
        skill_dir.mkdir(parents=True, exist_ok=True)

        manifest = SkillManifest(
            installed_at="2025-01-15T12:00:00Z",
            skill_id="owner/no-skillmd",
            git_repo="https://github.com/owner/repo",
            skill_path="skills/no-skillmd",
            git_sha="abc123",
            skilz_version="1.0.0",
            install_mode="copy",
        )

        mock_skill = InstalledSkill(
            skill_id="owner/no-skillmd",
            skill_name="no-skillmd",
            path=skill_dir,
            manifest=manifest,
            agent="claude",
            project_level=False,
        )

        args = argparse.Namespace(
            skill_name="no-skillmd",
            agent=None,
            project=False,
        )

        with patch("skilz.commands.read_cmd.find_installed_skill") as mock_find:
            mock_find.return_value = mock_skill

            result = cmd_read(args)

            assert result == 1

            captured = capsys.readouterr()
            assert "SKILL.md not found" in captured.err

    def test_read_with_agent_filter(self, mock_skill: InstalledSkill) -> None:
        """Test reading with agent filter."""
        args = argparse.Namespace(
            skill_name="test-skill",
            agent="claude",
            project=False,
        )

        with patch("skilz.commands.read_cmd.find_installed_skill") as mock_find:
            mock_find.return_value = mock_skill

            result = cmd_read(args)

            assert result == 0
            # Verify agent was passed to find_installed_skill
            mock_find.assert_called_with(
                skill_id_or_name="test-skill",
                agent="claude",
                project_level=False,
            )

    def test_read_project_level_fallback(self, mock_skill: InstalledSkill) -> None:
        """Test that user-level miss falls back to project-level across agents."""
        args = argparse.Namespace(
            skill_name="test-skill",
            agent=None,
            project=False,
        )

        with patch("skilz.commands.read_cmd.find_installed_skill") as mock_find:
            # With fallback search, we try all agents at user-level first (5 agents),
            # then all agents at project-level. Return skill on first project-level call.
            from skilz.commands.read_cmd import FALLBACK_SEARCH_ORDER

            num_agents = len(FALLBACK_SEARCH_ORDER)
            # All user-level calls return None, first project-level call returns skill
            mock_find.side_effect = [None] * num_agents + [mock_skill]

            result = cmd_read(args)

            assert result == 0
            # Should have tried all user-level agents + 1 project-level agent
            assert mock_find.call_count == num_agents + 1
            # Last call should have project_level=True
            _, kwargs = mock_find.call_args
            assert kwargs.get("project_level") is True

    def test_read_outputs_base_directory(
        self, mock_skill: InstalledSkill, capsys: pytest.CaptureFixture
    ) -> None:
        """Test that output includes base directory for resource resolution."""
        args = argparse.Namespace(
            skill_name="test-skill",
            agent=None,
            project=False,
        )

        with patch("skilz.commands.read_cmd.find_installed_skill") as mock_find:
            mock_find.return_value = mock_skill

            cmd_read(args)

            captured = capsys.readouterr()
            # Base directory should be included for resolving bundled resources
            assert "Base Directory:" in captured.out
            assert str(mock_skill.path) in captured.out


class TestCLIIntegration:
    """Test CLI integration for read command."""

    def test_read_command_exists(self) -> None:
        """Test that read command is registered in CLI."""
        from skilz.cli import create_parser

        parser = create_parser()
        # Parse read command
        args = parser.parse_args(["read", "some-skill"])

        assert args.command == "read"
        assert args.skill_name == "some-skill"

    def test_read_command_options(self) -> None:
        """Test read command accepts all expected options."""
        from skilz.cli import create_parser

        parser = create_parser()
        args = parser.parse_args(
            [
                "read",
                "my-skill",
                "--agent",
                "claude",
                "--project",
            ]
        )

        assert args.skill_name == "my-skill"
        assert args.agent == "claude"
        assert args.project is True


class TestFallbackSearch:
    """Tests for fallback directory search in read command."""

    def test_fallback_search_order_defined(self) -> None:
        """Test that FALLBACK_SEARCH_ORDER is defined and has expected agents."""
        from skilz.commands.read_cmd import FALLBACK_SEARCH_ORDER

        assert len(FALLBACK_SEARCH_ORDER) > 0
        assert "claude" in FALLBACK_SEARCH_ORDER
        assert "universal" in FALLBACK_SEARCH_ORDER

    def test_fallback_prefers_claude_over_universal(self) -> None:
        """Claude directory should be searched before universal directory."""
        from skilz.commands.read_cmd import FALLBACK_SEARCH_ORDER

        claude_idx = FALLBACK_SEARCH_ORDER.index("claude")
        universal_idx = FALLBACK_SEARCH_ORDER.index("universal")
        assert claude_idx < universal_idx

    def test_fallback_search_finds_skill_in_later_agent(self, mock_skill: InstalledSkill) -> None:
        """Test that fallback search finds skill in a later agent directory."""
        args = argparse.Namespace(
            skill_name="test-skill",
            agent=None,
            project=False,
        )

        with patch("skilz.commands.read_cmd.find_installed_skill") as mock_find:
            from skilz.commands.read_cmd import FALLBACK_SEARCH_ORDER

            # Skill not found in first few agents, found in 3rd agent
            mock_find.side_effect = [None, None, mock_skill]

            result = cmd_read(args)

            assert result == 0
            # Should have called find_installed_skill 3 times
            assert mock_find.call_count == 3
            # Third call should be for the 3rd agent in fallback order
            third_call_args = mock_find.call_args_list[2]
            assert third_call_args[1]["agent"] == FALLBACK_SEARCH_ORDER[2]

    def test_agent_specified_skips_fallback(self, mock_skill: InstalledSkill) -> None:
        """Test that specifying --agent skips fallback search."""
        args = argparse.Namespace(
            skill_name="test-skill",
            agent="gemini",
            project=False,
        )

        with patch("skilz.commands.read_cmd.find_installed_skill") as mock_find:
            mock_find.return_value = mock_skill

            result = cmd_read(args)

            assert result == 0
            # Should only call once with the specified agent
            assert mock_find.call_count == 1
            assert mock_find.call_args[1]["agent"] == "gemini"
