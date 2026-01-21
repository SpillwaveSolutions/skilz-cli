"""Read command implementation.

This command reads and outputs skill content for AI agents to consume.
It follows the agentskills.io standard for skill invocation:
    skilz read <skill-name>
"""

import argparse
import sys

from skilz.agents import ExtendedAgentType
from skilz.scanner import find_installed_skill

# Fallback search order when --agent is not specified
# Searches directories in order until skill is found
FALLBACK_SEARCH_ORDER: list[ExtendedAgentType] = [
    "claude",  # .claude/skills/
    "universal",  # .skilz/skills/
    "gemini",  # .skilz/skills/ (gemini uses .skilz for project)
    "opencode",  # .opencode/skill/ or .skilz/skills/
    "codex",  # .codex/skills/
]


def cmd_read(args: argparse.Namespace) -> int:
    """
    Handle the read command.

    Finds an installed skill by name/ID and outputs:
    1. The base directory path (for resolving bundled resources)
    2. The full contents of SKILL.md

    Args:
        args: Parsed command-line arguments.

    Returns:
        Exit code (0 for success, non-zero for error).
    """
    skill_name: str = args.skill_name
    agent = getattr(args, "agent", None)
    project_level: bool = getattr(args, "project", False)

    skill = None

    if agent:
        # Agent specified - search only that agent's directories
        skill = find_installed_skill(
            skill_id_or_name=skill_name,
            agent=agent,
            project_level=project_level,
        )
        # Try project-level if user-level not found
        if skill is None and not project_level:
            skill = find_installed_skill(
                skill_id_or_name=skill_name,
                agent=agent,
                project_level=True,
            )
    else:
        # No agent specified - use fallback search across multiple directories
        # First try user-level for agents that support it
        for fallback_agent in FALLBACK_SEARCH_ORDER:
            skill = find_installed_skill(
                skill_id_or_name=skill_name,
                agent=fallback_agent,
                project_level=False,  # Try user-level first
            )
            if skill is not None:
                break

        # If not found at user-level, try project-level
        if skill is None:
            for fallback_agent in FALLBACK_SEARCH_ORDER:
                skill = find_installed_skill(
                    skill_id_or_name=skill_name,
                    agent=fallback_agent,
                    project_level=True,
                )
                if skill is not None:
                    break

    if skill is None:
        print(f"Error: Skill '{skill_name}' not found.", file=sys.stderr)
        print(
            "Use 'skilz list' to see installed skills or 'skilz install' to install.",
            file=sys.stderr,
        )
        return 1

    # Check if skill is broken
    if skill.is_broken:
        print(f"Error: Skill '{skill_name}' has a broken symlink.", file=sys.stderr)
        print(
            f"Target: {skill.canonical_path or 'unknown'}",
            file=sys.stderr,
        )
        return 1

    # Resolve the actual skill directory (follow symlink if needed)
    skill_dir = skill.canonical_path if skill.canonical_path else skill.path

    # Look for SKILL.md
    skill_md_path = skill_dir / "SKILL.md"
    if not skill_md_path.exists():
        print(f"Error: SKILL.md not found in {skill_dir}", file=sys.stderr)
        return 1

    # Read the SKILL.md content
    try:
        content = skill_md_path.read_text()
    except OSError as e:
        print(f"Error reading SKILL.md: {e}", file=sys.stderr)
        return 1

    # Output in a format suitable for AI agent consumption
    print(f"# Skill: {skill.skill_name}")
    print(f"# Base Directory: {skill_dir}")
    print(f"# SKILL.md Path: {skill_md_path}")
    print()
    print(content)

    return 0
