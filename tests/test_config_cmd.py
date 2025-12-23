"""Tests for the config command."""

import argparse
import json
from unittest.mock import patch

import pytest

from skilz import config
from skilz.commands.config_cmd import (
    cmd_config,
    cmd_config_init,
    cmd_config_show,
    format_value,
    prompt_choice,
    prompt_value,
)


@pytest.fixture
def mock_config_path(tmp_path):
    """Mock the config path to use temp directory."""
    config_dir = tmp_path / ".config" / "skilz"
    config_dir.mkdir(parents=True)
    config_file = config_dir / "settings.json"
    with patch.object(config, "CONFIG_DIR", config_dir):
        with patch.object(config, "CONFIG_PATH", config_file):
            yield config_file


class TestFormatValue:
    """Tests for format_value function."""

    def test_format_none(self):
        """Should format None as '(not set)'."""
        assert format_value(None) == "(not set)"

    def test_format_short_value(self):
        """Should not truncate short values."""
        assert format_value("short") == "short"

    def test_format_long_value(self):
        """Should truncate long values."""
        long_val = "a" * 50
        result = format_value(long_val, max_len=10)
        assert result == "aaaaaaa..."
        assert len(result) == 10


class TestPromptValue:
    """Tests for prompt_value function."""

    def test_prompt_accepts_input(self):
        """Should return user input."""
        with patch("builtins.input", return_value="custom_value"):
            result = prompt_value("Test", "default")
        assert result == "custom_value"

    def test_prompt_empty_returns_default(self):
        """Should return default on empty input."""
        with patch("builtins.input", return_value=""):
            result = prompt_value("Test", "default")
        assert result == "default"

    def test_prompt_keyboard_interrupt(self):
        """Should return None on keyboard interrupt."""
        with patch("builtins.input", side_effect=KeyboardInterrupt):
            result = prompt_value("Test", "default")
        assert result is None

    def test_prompt_with_validator(self):
        """Should validate input."""
        with patch("builtins.input", return_value="invalid"):
            result = prompt_value("Test", "default", validator=lambda x: x == "valid")
        assert result == "default"


class TestPromptChoice:
    """Tests for prompt_choice function."""

    def test_prompt_choice_valid(self):
        """Should accept valid choice."""
        with patch("builtins.input", return_value="option1"):
            result = prompt_choice("Test", ["option1", "option2"], "option2")
        assert result == "option1"

    def test_prompt_choice_empty_returns_default(self):
        """Should return default on empty input."""
        with patch("builtins.input", return_value=""):
            result = prompt_choice("Test", ["option1", "option2"], "option2")
        assert result == "option2"

    def test_prompt_choice_invalid_returns_default(self):
        """Should return default on invalid input."""
        with patch("builtins.input", return_value="invalid"):
            result = prompt_choice("Test", ["option1", "option2"], "option2")
        assert result == "option2"


class TestCmdConfigShow:
    """Tests for cmd_config_show function."""

    def test_show_no_config_file(self, mock_config_path, capsys):
        """Should show '(not created)' when config file doesn't exist."""
        args = argparse.Namespace(verbose=False)
        result = cmd_config_show(args)

        assert result == 0
        captured = capsys.readouterr()
        assert "(not created)" in captured.out

    def test_show_with_config_file(self, mock_config_path, capsys):
        """Should show config when file exists."""
        mock_config_path.write_text(
            json.dumps(
                {
                    "agent_default": "opencode",
                }
            )
        )

        args = argparse.Namespace(verbose=False)
        result = cmd_config_show(args)

        assert result == 0
        captured = capsys.readouterr()
        assert "opencode" in captured.out
        assert "(not created)" not in captured.out

    def test_show_displays_all_settings(self, mock_config_path, capsys):
        """Should display all configuration settings."""
        args = argparse.Namespace(verbose=False)
        cmd_config_show(args)

        captured = capsys.readouterr()
        assert "claude_code_home" in captured.out
        assert "open_code_home" in captured.out
        assert "agent_default" in captured.out

    def test_show_suggests_init(self, mock_config_path, capsys):
        """Should suggest running --init."""
        args = argparse.Namespace(verbose=False)
        cmd_config_show(args)

        captured = capsys.readouterr()
        assert "skilz config --init" in captured.out


class TestCmdConfigInit:
    """Tests for cmd_config_init function."""

    def test_init_with_yes_flag(self, mock_config_path, capsys):
        """Should use defaults with -y flag."""
        args = argparse.Namespace(verbose=False, yes=True, yes_all=False)
        result = cmd_config_init(args)

        assert result == 0
        captured = capsys.readouterr()
        assert "default configuration" in captured.out.lower()
        assert mock_config_path.exists()

    def test_init_with_yes_all_flag(self, mock_config_path, capsys):
        """Should use defaults with --yes-all flag."""
        args = argparse.Namespace(verbose=False, yes=False, yes_all=True)
        result = cmd_config_init(args)

        assert result == 0
        captured = capsys.readouterr()
        assert "default configuration" in captured.out.lower()

    def test_init_interactive_cancelled(self, mock_config_path, capsys):
        """Should handle cancelled interactive input."""
        args = argparse.Namespace(verbose=False, yes=False, yes_all=False)

        with patch("builtins.input", side_effect=KeyboardInterrupt):
            result = cmd_config_init(args)

        assert result == 0
        captured = capsys.readouterr()
        assert "Cancelled" in captured.out

    def test_init_interactive_completes(self, mock_config_path, capsys):
        """Should complete interactive setup."""
        args = argparse.Namespace(verbose=False, yes=False, yes_all=False)

        # Simulate entering values (including shell completion choice)
        inputs = iter(
            [
                "/custom/claude",  # Claude Code home
                "/custom/opencode",  # OpenCode home
                "opencode",  # Default agent
                "3",  # Skip shell completion
            ]
        )

        with patch("builtins.input", side_effect=lambda _: next(inputs)):
            result = cmd_config_init(args)

        assert result == 0
        captured = capsys.readouterr()
        assert "saved" in captured.out.lower()

        # Verify saved values
        with open(mock_config_path) as f:
            saved = json.load(f)
        assert saved["claude_code_home"] == "/custom/claude"
        assert saved["open_code_home"] == "/custom/opencode"
        assert saved["agent_default"] == "opencode"


class TestCmdConfig:
    """Tests for cmd_config function."""

    def test_config_without_init(self, mock_config_path, capsys):
        """Should call show when --init not specified."""
        args = argparse.Namespace(init=False, verbose=False)
        result = cmd_config(args)

        assert result == 0
        captured = capsys.readouterr()
        assert "Configuration:" in captured.out

    def test_config_with_init(self, mock_config_path, capsys):
        """Should call init when --init specified."""
        args = argparse.Namespace(init=True, verbose=False, yes=True, yes_all=False)
        result = cmd_config(args)

        assert result == 0
        captured = capsys.readouterr()
        assert "Configuration Setup" in captured.out
