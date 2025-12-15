"""Command-line interface for Skilz."""

import argparse
import sys

from skilz import __version__


def create_parser() -> argparse.ArgumentParser:
    """Create the argument parser for the CLI."""
    parser = argparse.ArgumentParser(
        prog="skilz",
        description="The universal package manager for AI skills.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  skilz install anthropics/web-artifacts-builder
  skilz install some-skill --agent opencode
  skilz list --agent claude
  skilz -y remove skill-id              # Skip confirmation (scripting)
  skilz config                          # Show configuration
  skilz --version

Common options (available on most commands):
  --agent {claude,opencode}   Target agent (auto-detected if not specified)
  --project                   Use project-level instead of user-level
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
        help="The skill ID to install (e.g., anthropics/web-artifacts-builder)",
    )
    install_parser.add_argument(
        "--agent",
        choices=["claude", "opencode"],
        default=None,
        help="Target agent (auto-detected if not specified)",
    )
    install_parser.add_argument(
        "--project",
        action="store_true",
        help="Install to project directory instead of user directory",
    )

    # List command
    list_parser = subparsers.add_parser(
        "list",
        help="List installed skills",
        description="Show all installed skills with their versions and status.",
    )
    list_parser.add_argument(
        "--agent",
        choices=["claude", "opencode"],
        default=None,
        help="Filter by agent type (auto-detected if not specified)",
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
        choices=["claude", "opencode"],
        default=None,
        help="Filter by agent type (auto-detected if not specified)",
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
        choices=["claude", "opencode"],
        default=None,
        help="Filter by agent type (auto-detected if not specified)",
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

    # Unknown command (shouldn't happen with subparsers)
    parser.print_help()
    return 1


if __name__ == "__main__":
    sys.exit(main())
