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
  skilz install anthropics/web-artifacts-builder          # Install from marketplace
  skilz install https://github.com/owner/repo             # Install from Git URL (auto-detect)
  skilz install -g https://github.com/owner/repo --all    # Install all skills from repo
  skilz install -f ~/skills/my-skill -p --agent gemini    # Install from local path
  skilz update                                            # Update all skills to latest versions
  skilz update anthropics/web-artifacts-builder           # Update specific skill
  skilz remove my-skill                                   # Remove a skill (with confirmation)
  skilz rm my-skill -y                                    # Remove without confirmation
  skilz search excel --limit 5                            # Search GitHub for skills
  skilz list --agent claude --json                        # List skills as JSON
  skilz list --all                                        # List skills from all agents
  skilz ls -p                                             # List project skills (alias)
  skilz read extracting-keywords                          # Read skill content for AI
  skilz config                                            # Show current configuration
  skilz config --init                                     # Run configuration setup
  skilz visit anthropics/skills                           # Open repo in browser

Common options (available on most commands):
  --agent AGENT     Target agent (auto-detected if not specified)
  -p, --project     Use project-level instead of user-level

Supported agents: {", ".join(agent_choices)}

For detailed help: skilz <command> --help
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
        help="Install skills from marketplace, Git, or local files",
        description="Install a skill by its ID from the registry, Git repository, or local path.",
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
        "-p",
        "--project",
        action="store_true",
        help="Install to project directory instead of user directory",
    )
    install_parser.add_argument(
        "--config",
        metavar="FILE",
        help="Config file to update (requires --project). Example: --config GEMINI.md",
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
    install_parser.add_argument(
        "--all",
        action="store_true",
        dest="install_all",
        help="Install all skills found in repository (with -g/--git)",
    )
    install_parser.add_argument(
        "--skill",
        metavar="NAME",
        help="Install specific skill by name from multi-skill repository (with -g/--git)",
    )
    install_parser.add_argument(
        "--force-config",
        action="store_true",
        dest="force_config",
        help="Force config file updates even for agents with native skill support",
    )

    # List command (alias: ls)
    list_parser = subparsers.add_parser(
        "list",
        help="List installed skills (alias: ls)",
        description="Show all installed skills with their versions, status, and agent information.",
    )
    list_parser.add_argument(
        "--agent",
        choices=agent_choices,
        default=None,
        metavar="AGENT",
        help=f"Filter by agent type: {{{agents_str}}} (auto-detected if not specified)",
    )
    list_parser.add_argument(
        "-p",
        "--project",
        action="store_true",
        help="List project-level skills instead of user-level",
    )
    list_parser.add_argument(
        "--json",
        action="store_true",
        help="Output as JSON",
    )
    list_parser.add_argument(
        "--all",
        action="store_true",
        help="Scan all agents (default: top 5)",
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
        "-p",
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
        "-p",
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
        help="Read skill content for AI consumption",
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
        "-p",
        "--project",
        action="store_true",
        help="Search project-level skills only",
    )

    # Visit command
    visit_parser = subparsers.add_parser(
        "visit",
        help="Open a skill's page in browser (marketplace or GitHub)",
        description="Open a skill's page in the default browser. "
        "By default opens the Skilzwave marketplace page, use -g/--git for GitHub.",
    )
    visit_parser.add_argument(
        "source",
        help="Source to visit: skill-id, owner/repo, owner/repo/skill, or full URL",
    )
    visit_parser.add_argument(
        "-g",
        "--git",
        action="store_true",
        help="Open GitHub page instead of marketplace (default: marketplace)",
    )
    visit_parser.add_argument(
        "--dry-run",
        action="store_true",
        dest="dry_run",
        help="Output the URL without opening browser",
    )

    # Search command
    search_parser = subparsers.add_parser(
        "search",
        help="Search GitHub for available skills",
        description="Search GitHub repositories for skills matching a query.",
    )
    search_parser.add_argument(
        "query",
        help="Search query (e.g., 'excel', 'pdf', 'data analysis')",
    )
    search_parser.add_argument(
        "-l",
        "--limit",
        type=int,
        default=10,
        help="Maximum number of results (default: 10)",
    )
    search_parser.add_argument(
        "--json",
        action="store_true",
        help="Output as JSON",
    )

    # Command aliases for Unix-like familiarity
    # ls alias for list
    ls_parser = subparsers.add_parser(
        "ls",
        help="Alias for 'list' - List installed skills",
        description="Show all installed skills with their versions and status.",
    )
    ls_parser.add_argument(
        "--agent",
        choices=agent_choices,
        default=None,
        metavar="AGENT",
        help=f"Filter by agent type: {{{agents_str}}} (auto-detected if not specified)",
    )
    ls_parser.add_argument(
        "-p",
        "--project",
        action="store_true",
        help="List project-level skills instead of user-level",
    )
    ls_parser.add_argument(
        "--json",
        action="store_true",
        help="Output as JSON",
    )

    # rm alias for remove/uninstall
    rm_parser = subparsers.add_parser(
        "rm",
        help="Alias for 'remove' - Remove a skill",
        description="Uninstall a skill by removing its directory.",
    )
    rm_parser.add_argument(
        "skill_id",
        help="Skill to remove (ID or name)",
    )
    rm_parser.add_argument(
        "--agent",
        choices=agent_choices,
        default=None,
        metavar="AGENT",
        help=f"Filter by agent type: {{{agents_str}}} (auto-detected if not specified)",
    )
    rm_parser.add_argument(
        "-p",
        "--project",
        action="store_true",
        help="Remove project-level skill instead of user-level",
    )
    rm_parser.add_argument(
        "-y",
        "--yes",
        action="store_true",
        help="Skip confirmation prompt",
    )

    # uninstall alias for remove
    uninstall_parser = subparsers.add_parser(
        "uninstall",
        help="Alias for 'remove' - Remove a skill",
        description="Uninstall a skill by removing its directory.",
    )
    uninstall_parser.add_argument(
        "skill_id",
        help="Skill to remove (ID or name)",
    )
    uninstall_parser.add_argument(
        "--agent",
        choices=agent_choices,
        default=None,
        metavar="AGENT",
        help=f"Filter by agent type: {{{agents_str}}} (auto-detected if not specified)",
    )
    uninstall_parser.add_argument(
        "-p",
        "--project",
        action="store_true",
        help="Remove project-level skill instead of user-level",
    )
    uninstall_parser.add_argument(
        "-y",
        "--yes",
        action="store_true",
        help="Skip confirmation prompt",
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

    if args.command in ("list", "ls"):
        from skilz.commands.list_cmd import cmd_list

        return cmd_list(args)

    if args.command == "update":
        from skilz.commands.update_cmd import cmd_update

        return cmd_update(args)

    if args.command in ("remove", "rm", "uninstall"):
        from skilz.commands.remove_cmd import cmd_remove

        return cmd_remove(args)

    if args.command == "config":
        from skilz.commands.config_cmd import cmd_config

        return cmd_config(args)

    if args.command == "read":
        from skilz.commands.read_cmd import cmd_read

        return cmd_read(args)

    if args.command == "visit":
        from skilz.commands.visit_cmd import cmd_visit

        return cmd_visit(args)

    if args.command == "search":
        from skilz.commands.search_cmd import cmd_search

        return cmd_search(args)

    # Unknown command (shouldn't happen with subparsers)
    parser.print_help()
    return 1


if __name__ == "__main__":
    sys.exit(main())
