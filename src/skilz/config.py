"""Configuration management for Skilz.

This module handles loading, saving, and merging configuration from:
1. Default values (hardcoded)
2. Config file (~/.config/skilz/settings.json)
3. Environment variables (CLAUDE_CODE_HOME, OPEN_CODE_HOME, AGENT_DEFAULT)
"""

import json
import os
from pathlib import Path
from typing import Any, cast

# Configuration file location (XDG standard)
CONFIG_DIR = Path.home() / ".config" / "skilz"
CONFIG_PATH = CONFIG_DIR / "settings.json"
REGISTRY_CONFIG_PATH = CONFIG_DIR / "config.json"

# Default configuration values
DEFAULTS: dict[str, str | None] = {
    "claude_code_home": str(Path.home() / ".claude"),
    "open_code_home": str(Path.home() / ".config" / "opencode"),
    "agent_default": None,  # None means auto-detect
}

# Environment variable names for each config key
ENV_VARS: dict[str, str] = {
    "claude_code_home": "CLAUDE_CODE_HOME",
    "open_code_home": "OPEN_CODE_HOME",
    "agent_default": "AGENT_DEFAULT",
}

# Valid agent values
VALID_AGENTS = {"claude", "opencode"}


def get_config_path() -> Path:
    """Get the path to the configuration file."""
    return CONFIG_PATH


def load_config() -> dict[str, str | None]:
    """
    Load configuration from file.

    Returns:
        Configuration dictionary. If file doesn't exist, returns defaults.
    """
    if not CONFIG_PATH.exists():
        return DEFAULTS.copy()

    try:
        with open(CONFIG_PATH) as f:
            file_config = json.load(f)

        # Merge with defaults (file overrides defaults)
        config = DEFAULTS.copy()
        for key in DEFAULTS:
            if key in file_config:
                config[key] = file_config[key]

        return config
    except (json.JSONDecodeError, OSError):
        # If file is corrupted or unreadable, return defaults
        return DEFAULTS.copy()


def get_effective_config() -> dict[str, str | None]:
    """
    Get effective configuration after applying environment variable overrides.

    Priority (lowest to highest):
    1. Default values
    2. Config file
    3. Environment variables

    Returns:
        Configuration dictionary with all overrides applied.
    """
    config = load_config()

    # Apply environment variable overrides
    for key, env_var in ENV_VARS.items():
        env_value = os.environ.get(env_var)
        if env_value is not None:
            # Validate agent_default
            if key == "agent_default" and env_value.lower() not in VALID_AGENTS:
                continue  # Ignore invalid agent values
            config[key] = env_value

    return config


def get_config_sources() -> dict[str, dict[str, Any]]:
    """
    Get configuration values with their sources for display.

    Returns:
        Dictionary mapping config keys to their values and sources.
        Format: {key: {"default": value, "file": value, "env": value, "effective": value}}
    """
    result = {}

    file_config = {}
    if CONFIG_PATH.exists():
        try:
            with open(CONFIG_PATH) as f:
                file_config = json.load(f)
        except (json.JSONDecodeError, OSError):
            pass

    for key in DEFAULTS:
        env_var = ENV_VARS.get(key)
        env_value = os.environ.get(env_var) if env_var else None

        # Determine effective value (priority: env > file > default)
        effective: str | None
        if env_value is not None:
            effective = env_value
        elif key in file_config:
            effective = file_config[key]
        else:
            effective = DEFAULTS[key]

        result[key] = {
            "default": DEFAULTS[key],
            "file": file_config.get(key),
            "env": env_value,
            "env_var": env_var,
            "effective": effective,
        }

    return result


def save_config(config: dict[str, str | None]) -> None:
    """
    Save configuration to file.

    Args:
        config: Configuration dictionary to save.

    Raises:
        OSError: If unable to write file.
    """
    # Create config directory if it doesn't exist
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)

    # Only save non-default values
    to_save = {}
    for key, value in config.items():
        if key in DEFAULTS and value != DEFAULTS[key]:
            to_save[key] = value
        elif key not in DEFAULTS:
            to_save[key] = value

    with open(CONFIG_PATH, "w") as f:
        json.dump(to_save, f, indent=2)


def get_claude_home() -> Path:
    """Get the Claude Code home directory from config."""
    config = get_effective_config()
    claude_home = config["claude_code_home"] or str(Path.home() / ".claude")
    return Path(claude_home).expanduser()


def get_opencode_home() -> Path:
    """Get the OpenCode home directory from config."""
    config = get_effective_config()
    opencode_home = config["open_code_home"] or str(Path.home() / ".config" / "opencode")
    return Path(opencode_home).expanduser()


def get_default_agent() -> str | None:
    """
    Get the default agent from config.

    Returns:
        Agent name ("claude" or "opencode") or None for auto-detect.
    """
    config = get_effective_config()
    agent = config.get("agent_default")

    if agent is None:
        return None

    # Validate and normalize
    agent_lower = agent.lower() if isinstance(agent, str) else None
    if agent_lower in VALID_AGENTS:
        return agent_lower

    return None


def config_exists() -> bool:
    """Check if configuration file exists."""
    return CONFIG_PATH.exists()


def get_registry_config_path() -> Path:
    """Get the path to the agent registry configuration file.

    Returns:
        Path to ~/.config/skilz/config.json
    """
    return REGISTRY_CONFIG_PATH


def load_registry_config() -> dict[str, Any] | None:
    """Load agent registry configuration from file.

    Returns:
        Parsed config dictionary, or None if file doesn't exist or is invalid.
    """
    if not REGISTRY_CONFIG_PATH.exists():
        return None

    try:
        with open(REGISTRY_CONFIG_PATH) as f:
            return cast(dict[str, Any], json.load(f))
    except (json.JSONDecodeError, OSError):
        # Corrupted or unreadable file
        return None


def registry_config_exists() -> bool:
    """Check if agent registry configuration file exists."""
    return REGISTRY_CONFIG_PATH.exists()
