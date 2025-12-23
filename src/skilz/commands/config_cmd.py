"""Config command implementation."""

import argparse
import sys
from collections.abc import Callable

from skilz.completion import get_shell_type, install_completion
from skilz.config import (
    CONFIG_PATH,
    DEFAULTS,
    VALID_AGENTS,
    config_exists,
    get_config_sources,
    get_effective_config,
    save_config,
)


def format_value(value: str | None, max_len: int = 30) -> str:
    """Format a value for display, truncating if needed."""
    if value is None:
        return "(not set)"
    val_str = str(value)
    if len(val_str) > max_len:
        return val_str[: max_len - 3] + "..."
    return val_str


def cmd_config_show(args: argparse.Namespace) -> int:
    """
    Show current configuration.

    Displays all configuration values with their sources (default, file, env).
    """
    verbose = getattr(args, "verbose", False)

    # Get config sources for detailed display
    sources = get_config_sources()

    # Header
    if config_exists():
        print(f"Configuration: {CONFIG_PATH}")
    else:
        print(f"Configuration: {CONFIG_PATH} (not created)")

    print()

    # Column headers
    print(f"{'Setting':<20} {'Config File':<18} {'Env Override':<18} {'Effective':<20}")
    print("-" * 76)

    # Display each setting
    for key in DEFAULTS:
        source = sources[key]
        file_val = format_value(source["file"], 16)
        env_val = format_value(source["env"], 16)
        effective_val = format_value(source["effective"], 18)

        # Show env var name in verbose mode
        if verbose and source["env_var"]:
            env_val = f"{env_val} ({source['env_var']})"

        print(f"{key:<20} {file_val:<18} {env_val:<18} {effective_val:<20}")

    print()
    print("Use 'skilz config --init' to create or modify configuration.")

    return 0


def prompt_value(
    prompt: str, default: str | None, validator: Callable[[str], bool] | None = None
) -> str | None:
    """
    Prompt user for a value with a default.

    Args:
        prompt: The prompt to display.
        default: Default value (shown in brackets).
        validator: Optional function to validate input.

    Returns:
        The entered value, or default if empty.
    """
    default_display = default if default else "none"
    try:
        value = input(f"{prompt} [{default_display}]: ").strip()
        if not value:
            return default
        if validator and not validator(value):
            print("Invalid value, using default.")
            return default
        return value
    except (EOFError, KeyboardInterrupt):
        print()
        return None


def prompt_choice(prompt: str, choices: list[str], default: str) -> str | None:
    """
    Prompt user to select from choices.

    Args:
        prompt: The prompt to display.
        choices: List of valid choices.
        default: Default choice.

    Returns:
        The selected choice.
    """
    choices_str = "/".join(choices)
    try:
        value = input(f"{prompt} ({choices_str}) [{default}]: ").strip().lower()
        if not value:
            return default
        if value in choices:
            return value
        print(f"Invalid choice. Using default: {default}")
        return default
    except (EOFError, KeyboardInterrupt):
        print()
        return None


def prompt_shell_completion() -> str | None:
    """
    Prompt user to install shell completion.

    Returns:
        Shell type to install ('zsh', 'bash') or None to skip.
    """
    detected_shell = get_shell_type()

    print()
    print("Install shell completion?")
    print("  [1] zsh (~/.zshrc)")
    print("  [2] bash (~/.bashrc)")
    print("  [3] Skip")
    print()

    default = "3"
    if detected_shell == "zsh":
        default = "1"
    elif detected_shell == "bash":
        default = "2"

    try:
        choice = input(f"Choice [{default}]: ").strip() or default
        if choice == "1":
            return "zsh"
        elif choice == "2":
            return "bash"
        return None
    except (EOFError, KeyboardInterrupt):
        print()
        return None


def cmd_config_init(args: argparse.Namespace) -> int:
    """
    Initialize or modify configuration interactively.

    With -y flag, uses defaults without prompting.
    """
    verbose = getattr(args, "verbose", False)
    yes_flag = getattr(args, "yes", False) or getattr(args, "yes_all", False)

    current_config = get_effective_config()

    print()
    print("Skilz Configuration Setup")
    print("-" * 26)
    print()

    if yes_flag:
        # Non-interactive: use defaults
        new_config = DEFAULTS.copy()
        print("Using default configuration...")
    else:
        # Interactive mode
        new_config = {}

        # Claude Code home
        claude_default = current_config.get("claude_code_home") or DEFAULTS["claude_code_home"]
        claude_home = prompt_value("Claude Code home", claude_default)
        if claude_home is None:
            print("Cancelled.")
            return 0
        new_config["claude_code_home"] = claude_home

        # OpenCode home
        opencode_default = current_config.get("open_code_home") or DEFAULTS["open_code_home"]
        opencode_home = prompt_value("OpenCode home", opencode_default)
        if opencode_home is None:
            print("Cancelled.")
            return 0
        new_config["open_code_home"] = opencode_home

        # Default agent
        agent_choices = ["claude", "opencode", "auto"]
        current_agent = current_config.get("agent_default")
        agent_default = current_agent if current_agent in VALID_AGENTS else "auto"
        agent = prompt_choice("Default agent", agent_choices, agent_default)
        if agent is None:
            print("Cancelled.")
            return 0
        new_config["agent_default"] = None if agent == "auto" else agent

    # Save configuration
    try:
        save_config(new_config)
        print()
        print(f"Configuration saved to {CONFIG_PATH}")

        if verbose:
            print()
            print("Saved values:")
            for key, value in new_config.items():
                if value != DEFAULTS.get(key):
                    print(f"  {key}: {value}")

    except OSError as e:
        print(f"Error saving configuration: {e}", file=sys.stderr)
        return 1

    # Offer shell completion (only in interactive mode)
    if not yes_flag:
        shell = prompt_shell_completion()
        if shell:
            success, message = install_completion(shell)
            if success:
                print(message)
            else:
                print(f"Warning: {message}", file=sys.stderr)

    return 0


def cmd_config(args: argparse.Namespace) -> int:
    """
    Handle the config command.

    Args:
        args: Parsed command-line arguments.

    Returns:
        Exit code (0 for success, non-zero for error).
    """
    init_flag = getattr(args, "init", False)

    if init_flag:
        return cmd_config_init(args)
    else:
        return cmd_config_show(args)
