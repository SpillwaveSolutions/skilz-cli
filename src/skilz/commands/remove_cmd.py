"""Remove command implementation."""

import argparse
import sys

from skilz.agents import AgentType, get_agent_display_name
from skilz.link_ops import remove_skill
from skilz.scanner import find_installed_skill


def confirm_remove(skill_id: str, agent: str) -> bool:
    """
    Prompt user to confirm skill removal.

    Args:
        skill_id: The skill ID to remove.
        agent: The agent display name.

    Returns:
        True if user confirms, False otherwise.
    """
    try:
        response = input(f"Remove {skill_id} from {agent}? [y/N] ")
        return response.strip().lower() in ("y", "yes")
    except (EOFError, KeyboardInterrupt):
        print()  # Newline after ^C
        return False


def cmd_remove(args: argparse.Namespace) -> int:
    """
    Handle the remove command.

    Args:
        args: Parsed command-line arguments.

    Returns:
        Exit code (0 for success, non-zero for error).
    """
    verbose = getattr(args, "verbose", False)
    yes_flag = getattr(args, "yes", False)
    yes_all = getattr(args, "yes_all", False)
    skip_confirm = yes_flag or yes_all
    agent: AgentType | None = getattr(args, "agent", None)
    project_level: bool = getattr(args, "project", False)
    skill_id: str = args.skill_id

    try:
        # Find the skill
        skill = find_installed_skill(
            skill_id,
            agent=agent,
            project_level=project_level,
        )

        if skill is None:
            print(f"Error: Skill '{skill_id}' not found.", file=sys.stderr)
            return 1

        agent_name = get_agent_display_name(skill.agent)

        # Check if it's a broken symlink
        if skill.is_broken:
            if verbose:
                print(f"Skill is a broken symlink (target: {skill.canonical_path})")

        # Check if it's a symlink
        is_symlink = skill.install_mode == "symlink"

        # Confirm removal
        if not skip_confirm:
            if is_symlink:
                confirm_msg = (
                    f"Remove symlink {skill_id} from {agent_name}? "
                    f"(Canonical copy at {skill.canonical_path} will be preserved)"
                )
                try:
                    response = input(f"{confirm_msg} [y/N] ")
                    if response.strip().lower() not in ("y", "yes"):
                        print("Cancelled.")
                        return 0
                except (EOFError, KeyboardInterrupt):
                    print()
                    return 0
            else:
                if not confirm_remove(skill.skill_id, agent_name):
                    print("Cancelled.")
                    return 0

        # Remove the skill using link_ops (handles symlink vs copy correctly)
        if verbose:
            mode = "symlink" if is_symlink else "copy"
            print(f"Removing {skill.path} (mode: {mode})...")

        remove_skill(skill.path)

        if is_symlink:
            print(f"Removed symlink: {skill.skill_id}")
        else:
            print(f"Removed: {skill.skill_id}")

        return 0

    except PermissionError as e:
        print(f"Error: Permission denied: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
