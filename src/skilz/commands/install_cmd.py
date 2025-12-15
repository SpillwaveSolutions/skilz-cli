"""Install command implementation."""

import argparse
import sys

from skilz.agents import AgentType
from skilz.errors import SkilzError


def cmd_install(args: argparse.Namespace) -> int:
    """
    Handle the install command.

    Args:
        args: Parsed command-line arguments.

    Returns:
        Exit code (0 for success, non-zero for error).
    """
    # Import here to avoid circular imports and speed up --help
    from skilz.installer import install_skill

    verbose = getattr(args, "verbose", False)
    agent: AgentType | None = getattr(args, "agent", None)
    project_level: bool = getattr(args, "project", False)
    skill_id: str = args.skill_id

    try:
        install_skill(
            skill_id=skill_id,
            agent=agent,
            project_level=project_level,
            verbose=verbose,
        )
        return 0
    except SkilzError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        return 1
