"""List command implementation."""

import argparse
import json
import sys
from pathlib import Path

from skilz.agents import AgentType, get_agent_display_name
from skilz.registry import lookup_skill, get_registry_paths
from skilz.scanner import InstalledSkill, scan_installed_skills


def get_skill_status(skill: InstalledSkill, verbose: bool = False) -> str:
    """
    Determine the status of an installed skill by comparing to registry.

    Args:
        skill: The installed skill to check.
        verbose: If True, print debug info.

    Returns:
        Status string: "up-to-date", "outdated", or "unknown".
    """
    try:
        registry_skill = lookup_skill(skill.skill_id, verbose=verbose)

        if skill.manifest.git_sha == registry_skill.git_sha:
            return "up-to-date"
        else:
            return "outdated"

    except Exception:
        # Skill not in registry or registry not found
        return "unknown"


def format_table_output(skills: list[InstalledSkill], verbose: bool = False) -> str:
    """
    Format skills as a table for terminal output.

    Args:
        skills: List of installed skills.
        verbose: If True, include status info.

    Returns:
        Formatted table string.
    """
    if not skills:
        return "No skills installed."

    # Column headers
    headers = ["Skill", "Version", "Installed", "Status"]

    # Build rows
    rows: list[tuple[str, str, str, str]] = []
    for skill in skills:
        status = get_skill_status(skill, verbose=verbose)
        rows.append((
            skill.skill_id,
            skill.git_sha_short,
            skill.installed_at_short,
            status,
        ))

    # Calculate column widths
    col_widths = [
        max(len(headers[0]), max(len(r[0]) for r in rows)),
        max(len(headers[1]), max(len(r[1]) for r in rows)),
        max(len(headers[2]), max(len(r[2]) for r in rows)),
        max(len(headers[3]), max(len(r[3]) for r in rows)),
    ]

    # Build output
    lines: list[str] = []

    # Header line
    header_line = "  ".join(
        h.ljust(col_widths[i]) for i, h in enumerate(headers)
    )
    lines.append(header_line)

    # Separator line
    separator = "\u2500" * (sum(col_widths) + 6)  # Unicode box drawing char
    lines.append(separator)

    # Data rows
    for row in rows:
        row_line = "  ".join(
            val.ljust(col_widths[i]) for i, val in enumerate(row)
        )
        lines.append(row_line)

    return "\n".join(lines)


def format_json_output(skills: list[InstalledSkill], verbose: bool = False) -> str:
    """
    Format skills as JSON output.

    Args:
        skills: List of installed skills.
        verbose: If True, include status info.

    Returns:
        JSON string.
    """
    output = []

    for skill in skills:
        status = get_skill_status(skill, verbose=verbose)
        output.append({
            "skill_id": skill.skill_id,
            "skill_name": skill.skill_name,
            "git_sha": skill.manifest.git_sha,
            "installed_at": skill.manifest.installed_at,
            "status": status,
            "path": str(skill.path),
            "agent": skill.agent,
            "project_level": skill.project_level,
        })

    return json.dumps(output, indent=2)


def cmd_list(args: argparse.Namespace) -> int:
    """
    Handle the list command.

    Args:
        args: Parsed command-line arguments.

    Returns:
        Exit code (0 for success, non-zero for error).
    """
    verbose = getattr(args, "verbose", False)
    json_output = getattr(args, "json", False)
    agent: AgentType | None = getattr(args, "agent", None)
    project_level: bool = getattr(args, "project", False)

    if verbose:
        agent_name = get_agent_display_name(agent) if agent else "all agents"
        level = "project-level" if project_level else "user-level"
        print(f"Scanning for {level} skills in {agent_name}...")

    try:
        skills = scan_installed_skills(
            agent=agent,
            project_level=project_level,
        )

        if json_output:
            output = format_json_output(skills, verbose=verbose)
        else:
            output = format_table_output(skills, verbose=verbose)

        print(output)
        return 0

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
