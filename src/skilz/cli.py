"""Command-line interface for Skilz."""

import argparse
import sys

from skilz import __version__


def _get_agent_choices() -> list[str]:
    """Get list of valid agent names for CLI choices.

    Returns list of all registered agents, falling back to ["claude", "opencode"]
    if the registry is unavailable.
    """
    try:
        from skilz.agent_registry import get_agent_choices

        return get_agent_choices()
    except ImportError:
        return ["claude", "opencode"]


def create_parser() -> argparse.ArgumentParser:
    """Create the argument parser for the CLI."""
    # Get dynamic agent choices
    agent_choices = _get_agent_choices()
    if len(agent_choices) > 5:
        agents_str = ", ".join(agent_choices[:5]) + ", ..."
    else:
        agents_str = ", ".join(agent_choices)

    parser = argparse.ArgumentParser(
        prog="skilz",
        description="The universal package manager for AI skills.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=f"""
Examples:
  skilz install anthropics/web-artifacts-builder
  skilz install some-skill --agent opencode
  skilz install some-skill --agent gemini --project
  skilz list --agent claude
  skilz read extracting-keywords        # Load skill content for AI agents
  skilz -y remove skill-id              # Skip confirmation (scripting)
  skilz config                          # Show configuration
  skilz --version

Common options (available on most commands):
  --agent {{{agents_str}}}
                              Target agent (auto-detected if not specified)
  --project                   Use project-level instead of user-level

Supported agents: {", ".join(agent_choices)}
        """,
    )

    parser.add_argument(
        "-V",
        "--version",
        action="version",
        version=f"skilz {__version__}",
    )

    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Enable verbose output",
    )

    parser.add_argument(
        "-y",
        "--yes-all",
        action="store_true",
        dest="yes_all",
        help="Skip all confirmation prompts (for scripting)",
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Install command
    install_parser = subparsers.add_parser(
        "install",
        help="Install a skill from the registry",
        description="Install a skill by its ID from the registry.",
    )
    install_parser.add_argument(
        "skill_id",
        nargs="?",
        default=None,
        help="The skill ID to install (e.g., anthropics/web-artifacts-builder)",
    )
    install_parser.add_argument(
        "--agent",
        choices=agent_choices,
        default=None,
        metavar="AGENT",
        help=f"Target agent: {{{agents_str}}} (auto-detected if not specified)",
    )
    install_parser.add_argument(
        "--project",
        action="store_true",
        help="Install to project directory instead of user directory",
    )

    # Installation mode flags (mutually exclusive)
    mode_group = install_parser.add_mutually_exclusive_group()
    mode_group.add_argument(
        "--copy",
        action="store_true",
        help="Copy files directly to agent's skills directory",
    )
    mode_group.add_argument(
        "--symlink",
        action="store_true",
        help="Create symlink to canonical copy in ~/.skilz/skills/",
    )

    # Source options (mutually exclusive with skill_id, handled in cmd)
    install_parser.add_argument(
        "-f",
        "--file",
        metavar="PATH",
        help="Install from a local filesystem path",
    )
    install_parser.add_argument(
        "-g",
        "--git",
        metavar="URL",
        help="Install from a git repository URL",
    )
    install_parser.add_argument(
        "--version",
        dest="version_spec",
        metavar="VERSION",
        help=(
            "Version to install: 'latest' (latest from main), "
            "'branch:NAME' (latest from branch), "
            "SHA (specific commit), or TAG (e.g., 1.0.1 -> v1.0.1). "
            "Default: use marketplace version"
        ),
    )

    # List command
    list_parser = subparsers.add_parser(
        "list",
        help="List installed skills",
        description="Show all installed skills with their versions and status.",
    )
    list_parser.add_argument(
        "--agent",
        choices=agent_choices,
        default=None,
        metavar="AGENT",
        help=f"Filter by agent type: {{{agents_str}}} (auto-detected if not specified)",
    )
    list_parser.add_argument(
        "--project",
        action="store_true",
        help="List project-level skills instead of user-level",
    )
    list_parser.add_argument(
        "--json",
        action="store_true",
        help="Output as JSON",
    )

    # Update command
    update_parser = subparsers.add_parser(
        "update",
        help="Update installed skills to latest versions",
        description="Update skills to match the registry. Updates all or a specific skill.",
    )
    update_parser.add_argument(
        "skill_id",
        nargs="?",
        default=None,
        help="Specific skill to update (updates all if not specified)",
    )
    update_parser.add_argument(
        "--agent",
        choices=agent_choices,
        default=None,
        metavar="AGENT",
        help=f"Filter by agent type: {{{agents_str}}} (auto-detected if not specified)",
    )
    update_parser.add_argument(
        "--project",
        action="store_true",
        help="Update project-level skills instead of user-level",
    )
    update_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be updated without making changes",
    )

    # Remove command
    remove_parser = subparsers.add_parser(
        "remove",
        help="Remove an installed skill",
        description="Uninstall a skill by removing its directory.",
    )
    remove_parser.add_argument(
        "skill_id",
        help="Skill to remove (ID or name)",
    )
    remove_parser.add_argument(
        "--agent",
        choices=agent_choices,
        default=None,
        metavar="AGENT",
        help=f"Filter by agent type: {{{agents_str}}} (auto-detected if not specified)",
    )
    remove_parser.add_argument(
        "--project",
        action="store_true",
        help="Remove project-level skill instead of user-level",
    )
    remove_parser.add_argument(
        "-y",
        "--yes",
        action="store_true",
        help="Skip confirmation prompt",
    )

    # Config command
    config_parser = subparsers.add_parser(
        "config",
        help="Show or modify configuration",
        description="View current configuration or run setup wizard.",
    )
    config_parser.add_argument(
        "--init",
        action="store_true",
        help="Run interactive configuration setup (or use -y for defaults)",
    )

    # Read command
    read_parser = subparsers.add_parser(
        "read",
        help="Read and output skill content",
        description="Load a skill's SKILL.md content for AI agent consumption.",
    )
    read_parser.add_argument(
        "skill_name",
        help="The skill name or ID to read (e.g., 'extracting-keywords')",
    )
    read_parser.add_argument(
        "--agent",
        choices=agent_choices,
        default=None,
        metavar="AGENT",
        help=f"Filter by agent type: {{{agents_str}}} (searches all if not specified)",
    )
    read_parser.add_argument(
        "--project",
        action="store_true",
        help="Search project-level skills only",
    )

    return parser


def main(argv: list[str] | None = None) -> int:
    """Main entry point for the CLI."""
    parser = create_parser()
    args = parser.parse_args(argv)

    if args.command is None:
        parser.print_help()
        return 0

    if args.command == "install":
        from skilz.commands.install_cmd import cmd_install

        return cmd_install(args)

    if args.command == "list":
        from skilz.commands.list_cmd import cmd_list

        return cmd_list(args)

    if args.command == "update":
        from skilz.commands.update_cmd import cmd_update

        return cmd_update(args)

    if args.command == "remove":
        from skilz.commands.remove_cmd import cmd_remove

        return cmd_remove(args)

    if args.command == "config":
        from skilz.commands.config_cmd import cmd_config

        return cmd_config(args)

    if args.command == "read":
        from skilz.commands.read_cmd import cmd_read

        return cmd_read(args)

    # Unknown command (shouldn't happen with subparsers)
    parser.print_help()
    return 1


if __name__ == "__main__":
    sys.exit(main())
