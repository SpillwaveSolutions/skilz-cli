"""Tests for the agents module."""

import json
from pathlib import Path
from unittest.mock import patch

import pytest

from skilz import config
from skilz.agents import (
    detect_agent,
    ensure_skills_dir,
    get_agent_display_name,
    get_agent_paths,
    get_skills_dir,
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

    def test_detect_gemini_from_project_dir(self, temp_dir, monkeypatch):
        """Detect Gemini from .gemini in project directory (SKILZ-49)."""
        # Create a fake home without claude
        fake_home = temp_dir / "home"
        fake_home.mkdir()
        monkeypatch.setattr(Path, "home", lambda: fake_home)

        (temp_dir / ".gemini").mkdir()

        agent = detect_agent(temp_dir)

        assert agent == "gemini"

    def test_detect_gemini_from_user_dir(self, temp_dir, monkeypatch):
        """Detect Gemini from ~/.gemini (SKILZ-49)."""
        # Create a fake home with .gemini but no .claude
        fake_home = temp_dir / "home"
        (fake_home / ".gemini").mkdir(parents=True)
        monkeypatch.setattr(Path, "home", lambda: fake_home)

        # Use a different temp dir as project dir (no .gemini there)
        project_dir = temp_dir / "project"
        project_dir.mkdir()

        agent = detect_agent(project_dir)

        assert agent == "gemini"

    def test_detect_gemini_priority_over_claude(self, temp_dir, monkeypatch):
        """Gemini takes priority over Claude when both present (Issue #49 popularity order)."""
        # Create both .claude and .gemini in project
        (temp_dir / ".claude").mkdir()
        (temp_dir / ".gemini").mkdir()

        agent = detect_agent(temp_dir)

        # Gemini should be detected first (highest priority in Issue #49 table)
        assert agent == "gemini"

    def test_detect_codex_from_project_dir(self, temp_dir, monkeypatch):
        """Detect Codex from .codex in project directory (BUG-001)."""
        # Create a fake home without claude or gemini
        fake_home = temp_dir / "home"
        fake_home.mkdir()
        monkeypatch.setattr(Path, "home", lambda: fake_home)

        (temp_dir / ".codex").mkdir()

        agent = detect_agent(temp_dir)

        assert agent == "codex"

    def test_detect_codex_from_user_dir(self, temp_dir, monkeypatch):
        """Detect Codex from ~/.codex (BUG-001)."""
        # Create a fake home with .codex but no .claude or .gemini
        fake_home = temp_dir / "home"
        (fake_home / ".codex").mkdir(parents=True)
        monkeypatch.setattr(Path, "home", lambda: fake_home)

        # Use a different temp dir as project dir (no .codex there)
        project_dir = temp_dir / "project"
        project_dir.mkdir()

        agent = detect_agent(project_dir)

        assert agent == "codex"

    def test_detect_gemini_priority_over_codex(self, temp_dir, monkeypatch):
        """Gemini takes priority over Codex when both present (BUG-001)."""
        # Create a fake home without claude
        fake_home = temp_dir / "home"
        fake_home.mkdir()
        monkeypatch.setattr(Path, "home", lambda: fake_home)

        # Create both .gemini and .codex in project
        (temp_dir / ".gemini").mkdir()
        (temp_dir / ".codex").mkdir()

        agent = detect_agent(temp_dir)

        # Gemini should be detected first
        assert agent == "gemini"

    def test_detect_opencode(self, temp_dir, monkeypatch):
        """Detect OpenCode from ~/.config/opencode."""
        # Create a fake home with opencode but no claude or gemini
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
        assert "skill" in str(path)  # singular for opencode

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
        # Registry uses "OpenCode CLI" as the display name
        assert get_agent_display_name("opencode") == "OpenCode CLI"

    def test_unknown_returns_raw(self):
        """Unknown agent returns raw value."""
        assert get_agent_display_name("unknown") == "unknown"  # type: ignore


class TestConfigIntegration:
    """Tests for config integration with agents module."""

    @pytest.fixture
    def mock_config_path(self, tmp_path):
        """Mock the config path to use temp directory."""
        config_dir = tmp_path / ".config" / "skilz"
        config_dir.mkdir(parents=True)
        config_file = config_dir / "settings.json"
        with patch.object(config, "CONFIG_DIR", config_dir):
            with patch.object(config, "CONFIG_PATH", config_file):
                yield config_file

    def test_detect_agent_uses_config_default(self, mock_config_path, temp_dir, monkeypatch):
        """detect_agent should return agent_default from config when set."""
        # Set up config with opencode as default
        mock_config_path.write_text(
            json.dumps(
                {
                    "agent_default": "opencode",
                }
            )
        )

        # Create fake home with nothing
        fake_home = temp_dir / "home"
        fake_home.mkdir()
        monkeypatch.setattr(Path, "home", lambda: fake_home)

        # Even though nothing is detected, config should return opencode
        project_dir = temp_dir / "project"
        project_dir.mkdir()
        agent = detect_agent(project_dir)

        assert agent == "opencode"

    def test_detect_agent_uses_config_claude_default(self, mock_config_path, temp_dir, monkeypatch):
        """detect_agent should return claude from config when set."""
        mock_config_path.write_text(
            json.dumps(
                {
                    "agent_default": "claude",
                }
            )
        )

        fake_home = temp_dir / "home"
        (fake_home / ".config" / "opencode").mkdir(parents=True)  # OpenCode installed
        monkeypatch.setattr(Path, "home", lambda: fake_home)

        project_dir = temp_dir / "project"
        project_dir.mkdir()

        # Config says claude, should override detection
        agent = detect_agent(project_dir)
        assert agent == "claude"

    def test_detect_agent_ignores_invalid_config_default(
        self, mock_config_path, temp_dir, monkeypatch
    ):
        """detect_agent should ignore invalid agent_default in config."""
        mock_config_path.write_text(
            json.dumps(
                {
                    "agent_default": "invalid_agent",
                }
            )
        )

        fake_home = temp_dir / "home"
        fake_home.mkdir()
        monkeypatch.setattr(Path, "home", lambda: fake_home)

        project_dir = temp_dir / "project"
        project_dir.mkdir()

        # Invalid config, should fall back to default
        agent = detect_agent(project_dir)
        assert agent == "claude"

    def test_get_agent_paths_uses_config(self, mock_config_path, tmp_path):
        """get_agent_paths should use custom paths from config."""
        custom_claude = tmp_path / "custom_claude"
        custom_opencode = tmp_path / "custom_opencode"

        mock_config_path.write_text(
            json.dumps(
                {
                    "claude_code_home": str(custom_claude),
                    "open_code_home": str(custom_opencode),
                }
            )
        )

        paths = get_agent_paths()

        assert paths["claude"]["user"] == custom_claude / "skills"
        assert paths["opencode"]["user"] == custom_opencode / "skill"  # singular

    def test_get_skills_dir_uses_config_paths(self, mock_config_path, tmp_path):
        """get_skills_dir should use config paths for user-level."""
        custom_claude = tmp_path / "custom_claude"

        mock_config_path.write_text(
            json.dumps(
                {
                    "claude_code_home": str(custom_claude),
                }
            )
        )

        skills_dir = get_skills_dir("claude", project_level=False)

        assert skills_dir == custom_claude / "skills"

    def test_config_env_override_affects_agents(self, mock_config_path, monkeypatch, tmp_path):
        """Environment variables should override config and affect agent paths."""
        env_claude_home = tmp_path / "env_claude"

        monkeypatch.setenv("CLAUDE_CODE_HOME", str(env_claude_home))

        paths = get_agent_paths()

        assert paths["claude"]["user"] == env_claude_home / "skills"


class TestNewAgentDetection:
    """Tests for new agent detection (Issues #46, #47, #49)."""

    def test_detect_qwen_from_project_dir(self, temp_dir):
        """Detect Qwen Code from .qwen in project directory (Issue #46)."""
        (temp_dir / ".qwen").mkdir()

        agent = detect_agent(temp_dir)

        assert agent == "qwen"

    def test_detect_antigravity_from_project_dir(self, temp_dir):
        """Detect Antigravity from .agent in project directory (Issue #47)."""
        (temp_dir / ".agent").mkdir()

        agent = detect_agent(temp_dir)

        assert agent == "antigravity"

    def test_detect_openhands_from_project_dir(self, temp_dir):
        """Detect OpenHands from .openhands in project directory (Issue #49)."""
        (temp_dir / ".openhands").mkdir()

        agent = detect_agent(temp_dir)

        assert agent == "openhands"

    def test_detect_cline_from_project_dir(self, temp_dir):
        """Detect Cline from .cline in project directory (Issue #49)."""
        (temp_dir / ".cline").mkdir()

        agent = detect_agent(temp_dir)

        assert agent == "cline"

    def test_detect_goose_from_project_dir(self, temp_dir):
        """Detect Goose from .goose in project directory (Issue #49)."""
        (temp_dir / ".goose").mkdir()

        agent = detect_agent(temp_dir)

        assert agent == "goose"

    def test_detect_roo_from_project_dir(self, temp_dir):
        """Detect Roo Code from .roo in project directory (Issue #49)."""
        (temp_dir / ".roo").mkdir()

        agent = detect_agent(temp_dir)

        assert agent == "roo"

    def test_detect_kilo_from_project_dir(self, temp_dir):
        """Detect Kilo Code from .kilocode in project directory (Issue #49)."""
        (temp_dir / ".kilocode").mkdir()

        agent = detect_agent(temp_dir)

        assert agent == "kilo"

    def test_detect_trae_from_project_dir(self, temp_dir):
        """Detect Trae from .trae in project directory (Issue #49)."""
        (temp_dir / ".trae").mkdir()

        agent = detect_agent(temp_dir)

        assert agent == "trae"

    def test_detect_droid_from_project_dir(self, temp_dir):
        """Detect Droid from .factory in project directory (Issue #49)."""
        (temp_dir / ".factory").mkdir()

        agent = detect_agent(temp_dir)

        assert agent == "droid"

    def test_detect_kiro_cli_from_project_dir(self, temp_dir):
        """Detect Kiro CLI from .kiro in project directory (Issue #49)."""
        (temp_dir / ".kiro").mkdir()

        agent = detect_agent(temp_dir)

        assert agent == "kiro-cli"

    def test_detect_pi_from_project_dir(self, temp_dir):
        """Detect Pi from .pi in project directory (Issue #49)."""
        (temp_dir / ".pi").mkdir()

        agent = detect_agent(temp_dir)

        assert agent == "pi"

    def test_detect_neovate_from_project_dir(self, temp_dir):
        """Detect Neovate from .neovate in project directory (Issue #49)."""
        (temp_dir / ".neovate").mkdir()

        agent = detect_agent(temp_dir)

        assert agent == "neovate"

    def test_detect_windsurf_from_project_dir(self, temp_dir):
        """Detect Windsurf from .windsurf in project directory (Issue #49)."""
        (temp_dir / ".windsurf").mkdir()

        agent = detect_agent(temp_dir)

        assert agent == "windsurf"

    def test_detect_zencoder_from_project_dir(self, temp_dir):
        """Detect Zencoder from .zencoder in project directory (Issue #49)."""
        (temp_dir / ".zencoder").mkdir()

        agent = detect_agent(temp_dir)

        assert agent == "zencoder"

    def test_detect_amp_from_project_dir(self, temp_dir):
        """Detect Amp from .agents in project directory (Issue #49)."""
        (temp_dir / ".agents").mkdir()

        agent = detect_agent(temp_dir)

        assert agent == "amp"

    def test_detect_qoder_from_project_dir(self, temp_dir):
        """Detect Qoder from .qoder in project directory (Issue #49)."""
        (temp_dir / ".qoder").mkdir()

        agent = detect_agent(temp_dir)

        assert agent == "qoder"

    def test_detect_command_code_from_project_dir(self, temp_dir):
        """Detect Command Code from .commandcode in project directory (Issue #49)."""
        (temp_dir / ".commandcode").mkdir()

        agent = detect_agent(temp_dir)

        assert agent == "command-code"

    def test_detect_clawdbot_from_skills_dir(self, temp_dir):
        """Detect Clawdbot from skills/ directory with SKILL.md files (Issue #49)."""
        skills_dir = temp_dir / "skills"
        skills_dir.mkdir()

        # Create a skill directory with SKILL.md to simulate Clawdbot
        skill_dir = skills_dir / "test-skill"
        skill_dir.mkdir()
        (skill_dir / "SKILL.md").write_text("# Test Skill")

        agent = detect_agent(temp_dir)

        assert agent == "clawdbot"

    def test_detect_priority_order(self, temp_dir):
        """Test that detection follows priority order from Issue #49 table."""
        # Create multiple agent markers - Gemini should win (highest priority)
        (temp_dir / ".gemini").mkdir()
        (temp_dir / ".claude").mkdir()
        (temp_dir / ".qwen").mkdir()

        agent = detect_agent(temp_dir)

        assert agent == "gemini"  # Highest priority in Issue #49 table

    def test_detect_opencode_priority(self, temp_dir):
        """Test that OpenCode has high priority after Gemini."""
        (temp_dir / ".opencode").mkdir()
        (temp_dir / ".claude").mkdir()
        (temp_dir / ".qwen").mkdir()

        agent = detect_agent(temp_dir)

        assert agent == "opencode"  # Second highest priority
