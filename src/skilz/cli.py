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
  skilz --version
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

    return parser


def cmd_install(args: argparse.Namespace) -> int:
    """Handle the install command."""
    # Import here to avoid circular imports and speed up --help
    from skilz.installer import install_skill

    try:
        install_skill(
            skill_id=args.skill_id,
            agent=args.agent,
            project_level=args.project,
            verbose=args.verbose,
        )
        return 0
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def main(argv: list[str] | None = None) -> int:
    """Main entry point for the CLI."""
    parser = create_parser()
    args = parser.parse_args(argv)

    if args.command is None:
        parser.print_help()
        return 0

    if args.command == "install":
        return cmd_install(args)

    # Unknown command (shouldn't happen with subparsers)
    parser.print_help()
    return 1


if __name__ == "__main__":
    sys.exit(main())
