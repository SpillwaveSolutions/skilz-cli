"""Install command implementation."""

import argparse
import sys
from pathlib import Path
from typing import Literal

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
    from skilz.installer import install_local_skill, install_skill

    verbose = getattr(args, "verbose", False)
    agent: AgentType | None = getattr(args, "agent", None)
    project_level: bool = getattr(args, "project", False)
    skill_id: str | None = getattr(args, "skill_id", None)
    version_spec: str | None = getattr(args, "version_spec", None)

    # Handle source options
    file_path: str | None = getattr(args, "file", None)
    git_url: str | None = getattr(args, "git", None)

    # Validate source - exactly one of skill_id, -f, or -g must be provided
    sources = [s for s in [skill_id, file_path, git_url] if s is not None]
    if len(sources) == 0:
        print("Error: Must specify skill_id, --file, or --git", file=sys.stderr)
        return 1
    if len(sources) > 1:
        print("Error: Cannot use both skill_id and --file/--git options", file=sys.stderr)
        return 1

    # Determine installation mode from flags
    mode: Literal["copy", "symlink"] | None = None
    if getattr(args, "copy", False):
        mode = "copy"
    elif getattr(args, "symlink", False):
        mode = "symlink"

    # Handle -f and -g options
    if file_path is not None:
        try:
            install_local_skill(
                source_path=Path(file_path),
                agent=agent,
                project_level=project_level,
                verbose=verbose,
                mode=mode,
            )
            return 0
        except SkilzError as e:
            print(f"Error: {e}", file=sys.stderr)
            return 1
        except Exception as e:
            print(f"Unexpected error: {e}", file=sys.stderr)
            return 1

    if git_url is not None:
        print("Error: --git option not yet implemented", file=sys.stderr)
        return 1

    try:
        install_skill(
            skill_id=skill_id,  # type: ignore[arg-type]
            agent=agent,
            project_level=project_level,
            verbose=verbose,
            mode=mode,
            version_spec=version_spec,
        )
        return 0
    except SkilzError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        return 1
