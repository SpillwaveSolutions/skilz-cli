"""Tests for the agents module."""

import pytest
from pathlib import Path

from skilz.agents import (
    detect_agent,
    get_skills_dir,
    ensure_skills_dir,
    get_agent_display_name,
)


class TestDetectAgent:
    """Tests for detect_agent function."""

    def test_detect_claude_from_project_dir(self, temp_dir):
        """Detect Claude Code from .claude in project directory."""
        (temp_dir / ".claude").mkdir()

        agent = detect_agent(temp_dir)

        assert agent == "claude"

    def test_detect_claude_from_user_dir(self, temp_dir, monkeypatch):
        """Detect Claude Code from ~/.claude."""
        # Create a fake home with .claude
        fake_home = temp_dir / "home"
        (fake_home / ".claude").mkdir(parents=True)
        monkeypatch.setattr(Path, "home", lambda: fake_home)

        # Use a different temp dir as project dir (no .claude there)
        project_dir = temp_dir / "project"
        project_dir.mkdir()

        agent = detect_agent(project_dir)

        assert agent == "claude"

    def test_detect_opencode(self, temp_dir, monkeypatch):
        """Detect OpenCode from ~/.config/opencode."""
        # Create a fake home with opencode but no claude
        fake_home = temp_dir / "home"
        (fake_home / ".config" / "opencode").mkdir(parents=True)
        monkeypatch.setattr(Path, "home", lambda: fake_home)

        # Use a different temp dir as project dir
        project_dir = temp_dir / "project"
        project_dir.mkdir()

        agent = detect_agent(project_dir)

        assert agent == "opencode"

    def test_default_to_claude(self, temp_dir, monkeypatch):
        """Default to Claude when no agent detected."""
        # Create a fake home with nothing
        fake_home = temp_dir / "home"
        fake_home.mkdir()
        monkeypatch.setattr(Path, "home", lambda: fake_home)

        # Use empty project dir
        project_dir = temp_dir / "project"
        project_dir.mkdir()

        agent = detect_agent(project_dir)

        assert agent == "claude"


class TestGetSkillsDir:
    """Tests for get_skills_dir function."""

    def test_claude_user_dir(self):
        """Get Claude user skills directory."""
        path = get_skills_dir("claude", project_level=False)
        assert ".claude" in str(path)
        assert "skills" in str(path)

    def test_claude_project_dir(self, temp_dir):
        """Get Claude project skills directory."""
        path = get_skills_dir("claude", project_level=True, project_dir=temp_dir)
        assert ".claude" in str(path)
        assert "skills" in str(path)
        assert str(temp_dir) in str(path)

    def test_opencode_user_dir(self):
        """Get OpenCode user skills directory."""
        path = get_skills_dir("opencode", project_level=False)
        assert "opencode" in str(path)
        assert "skills" in str(path)

    def test_unknown_agent_raises_error(self):
        """Unknown agent raises ValueError."""
        with pytest.raises(ValueError):
            get_skills_dir("unknown_agent")  # type: ignore


class TestEnsureSkillsDir:
    """Tests for ensure_skills_dir function."""

    def test_creates_directory_if_missing(self, temp_dir, monkeypatch):
        """Create directory if it doesn't exist."""
        fake_home = temp_dir / "home"
        fake_home.mkdir()
        monkeypatch.setattr(Path, "home", lambda: fake_home)

        skills_dir = fake_home / ".claude" / "skills"
        assert not skills_dir.exists()

        result = ensure_skills_dir("claude", project_level=False)

        assert result.exists()
        assert result.is_dir()

    def test_returns_existing_directory(self, temp_dir):
        """Return existing directory without error for project-level."""
        # Use project-level to avoid home directory dependencies
        project_dir = temp_dir / "project"
        skills_dir = project_dir / ".claude" / "skills"
        skills_dir.mkdir(parents=True)

        result = ensure_skills_dir("claude", project_level=True, project_dir=project_dir)

        assert result.exists()
        assert result.is_dir()
        assert ".claude" in str(result)


class TestGetAgentDisplayName:
    """Tests for get_agent_display_name function."""

    def test_claude_display_name(self):
        """Get Claude Code display name."""
        assert get_agent_display_name("claude") == "Claude Code"

    def test_opencode_display_name(self):
        """Get OpenCode display name."""
        assert get_agent_display_name("opencode") == "OpenCode"

    def test_unknown_returns_raw(self):
        """Unknown agent returns raw value."""
        assert get_agent_display_name("unknown") == "unknown"  # type: ignore
