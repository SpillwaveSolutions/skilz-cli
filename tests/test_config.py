"""Tests for the config module."""

import json
import os
from pathlib import Path
from unittest.mock import patch

import pytest

from skilz import config


@pytest.fixture
def temp_config_dir(tmp_path):
    """Create a temporary config directory."""
    config_dir = tmp_path / ".config" / "skilz"
    config_dir.mkdir(parents=True)
    return config_dir


@pytest.fixture
def temp_config_file(temp_config_dir):
    """Create a temporary config file."""
    config_file = temp_config_dir / "settings.json"
    return config_file


@pytest.fixture
def mock_config_path(temp_config_dir, temp_config_file):
    """Mock the config path to use temp directory."""
    with patch.object(config, "CONFIG_DIR", temp_config_dir):
        with patch.object(config, "CONFIG_PATH", temp_config_file):
            yield temp_config_file


class TestLoadConfig:
    """Tests for load_config function."""

    def test_returns_defaults_when_no_file(self, mock_config_path):
        """Should return defaults when config file doesn't exist."""
        result = config.load_config()

        assert result["claude_code_home"] == str(Path.home() / ".claude")
        assert result["open_code_home"] == str(Path.home() / ".config" / "opencode")
        assert result["agent_default"] is None

    def test_loads_from_file(self, mock_config_path):
        """Should load values from config file."""
        mock_config_path.write_text(
            json.dumps(
                {
                    "claude_code_home": "/custom/claude",
                    "agent_default": "opencode",
                }
            )
        )

        result = config.load_config()

        assert result["claude_code_home"] == "/custom/claude"
        assert result["agent_default"] == "opencode"
        # open_code_home should still be default
        assert result["open_code_home"] == str(Path.home() / ".config" / "opencode")

    def test_handles_corrupted_file(self, mock_config_path):
        """Should return defaults when file is corrupted."""
        mock_config_path.write_text("not valid json")

        result = config.load_config()

        assert result == config.DEFAULTS


class TestGetEffectiveConfig:
    """Tests for get_effective_config function."""

    def test_returns_defaults_when_no_overrides(self, mock_config_path):
        """Should return defaults when no file or env vars."""
        with patch.dict(os.environ, {}, clear=True):
            result = config.get_effective_config()

        assert result["claude_code_home"] == str(Path.home() / ".claude")

    def test_file_overrides_defaults(self, mock_config_path):
        """Config file should override defaults."""
        mock_config_path.write_text(
            json.dumps(
                {
                    "claude_code_home": "/from/file",
                }
            )
        )

        with patch.dict(os.environ, {}, clear=True):
            result = config.get_effective_config()

        assert result["claude_code_home"] == "/from/file"

    def test_env_overrides_file(self, mock_config_path):
        """Environment variables should override file."""
        mock_config_path.write_text(
            json.dumps(
                {
                    "claude_code_home": "/from/file",
                }
            )
        )

        with patch.dict(os.environ, {"CLAUDE_CODE_HOME": "/from/env"}, clear=True):
            result = config.get_effective_config()

        assert result["claude_code_home"] == "/from/env"

    def test_env_overrides_defaults(self, mock_config_path):
        """Environment variables should override defaults."""
        with patch.dict(os.environ, {"OPEN_CODE_HOME": "/custom/opencode"}, clear=True):
            result = config.get_effective_config()

        assert result["open_code_home"] == "/custom/opencode"

    def test_agent_default_env_var(self, mock_config_path):
        """AGENT_DEFAULT env var should set agent_default."""
        with patch.dict(os.environ, {"AGENT_DEFAULT": "opencode"}, clear=True):
            result = config.get_effective_config()

        assert result["agent_default"] == "opencode"

    def test_invalid_agent_env_var_ignored(self, mock_config_path):
        """Invalid AGENT_DEFAULT values should be ignored."""
        with patch.dict(os.environ, {"AGENT_DEFAULT": "invalid"}, clear=True):
            result = config.get_effective_config()

        # Should still be None (default)
        assert result["agent_default"] is None


class TestGetConfigSources:
    """Tests for get_config_sources function."""

    def test_shows_all_sources(self, mock_config_path):
        """Should show values from all sources."""
        mock_config_path.write_text(
            json.dumps(
                {
                    "claude_code_home": "/from/file",
                }
            )
        )

        with patch.dict(os.environ, {"CLAUDE_CODE_HOME": "/from/env"}, clear=True):
            result = config.get_config_sources()

        claude_home = result["claude_code_home"]
        assert claude_home["default"] == str(Path.home() / ".claude")
        assert claude_home["file"] == "/from/file"
        assert claude_home["env"] == "/from/env"
        assert claude_home["effective"] == "/from/env"  # Env wins

    def test_shows_none_when_not_set(self, mock_config_path):
        """Should show None for unset sources."""
        with patch.dict(os.environ, {}, clear=True):
            result = config.get_config_sources()

        claude_home = result["claude_code_home"]
        assert claude_home["file"] is None
        assert claude_home["env"] is None


class TestSaveConfig:
    """Tests for save_config function."""

    def test_saves_to_file(self, mock_config_path):
        """Should save config to file."""
        config.save_config(
            {
                "claude_code_home": "/custom/path",
                "agent_default": "opencode",
            }
        )

        with open(mock_config_path) as f:
            saved = json.load(f)

        assert saved["claude_code_home"] == "/custom/path"
        assert saved["agent_default"] == "opencode"

    def test_creates_directory(self, tmp_path):
        """Should create config directory if needed."""
        config_dir = tmp_path / "new" / "config" / "dir"
        config_file = config_dir / "settings.json"

        with patch.object(config, "CONFIG_DIR", config_dir):
            with patch.object(config, "CONFIG_PATH", config_file):
                config.save_config({"agent_default": "claude"})

        assert config_dir.exists()
        assert config_file.exists()

    def test_only_saves_non_default_values(self, mock_config_path):
        """Should only save values that differ from defaults."""
        config.save_config(
            {
                "claude_code_home": str(Path.home() / ".claude"),  # Same as default
                "agent_default": "opencode",  # Different from default
            }
        )

        with open(mock_config_path) as f:
            saved = json.load(f)

        # Default value should not be saved
        assert "claude_code_home" not in saved
        # Non-default value should be saved
        assert saved["agent_default"] == "opencode"


class TestHelperFunctions:
    """Tests for helper functions."""

    def test_get_claude_home(self, mock_config_path):
        """get_claude_home should return Path."""
        mock_config_path.write_text(
            json.dumps(
                {
                    "claude_code_home": "/custom/claude",
                }
            )
        )

        result = config.get_claude_home()

        assert result == Path("/custom/claude")

    def test_get_opencode_home(self, mock_config_path):
        """get_opencode_home should return Path."""
        mock_config_path.write_text(
            json.dumps(
                {
                    "open_code_home": "/custom/opencode",
                }
            )
        )

        result = config.get_opencode_home()

        assert result == Path("/custom/opencode")

    def test_get_default_agent_none(self, mock_config_path):
        """get_default_agent should return None when not set."""
        result = config.get_default_agent()
        assert result is None

    def test_get_default_agent_claude(self, mock_config_path):
        """get_default_agent should return 'claude'."""
        mock_config_path.write_text(
            json.dumps(
                {
                    "agent_default": "claude",
                }
            )
        )

        result = config.get_default_agent()
        assert result == "claude"

    def test_get_default_agent_opencode(self, mock_config_path):
        """get_default_agent should return 'opencode'."""
        mock_config_path.write_text(
            json.dumps(
                {
                    "agent_default": "opencode",
                }
            )
        )

        result = config.get_default_agent()
        assert result == "opencode"

    def test_get_default_agent_invalid_returns_none(self, mock_config_path):
        """get_default_agent should return None for invalid values."""
        mock_config_path.write_text(
            json.dumps(
                {
                    "agent_default": "invalid",
                }
            )
        )

        result = config.get_default_agent()
        assert result is None

    def test_config_exists_true(self, mock_config_path):
        """config_exists should return True when file exists."""
        mock_config_path.write_text("{}")
        assert config.config_exists() is True

    def test_config_exists_false(self, mock_config_path):
        """config_exists should return False when file doesn't exist."""
        assert config.config_exists() is False
