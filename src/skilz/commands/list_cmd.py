"""List command implementation."""

import argparse
import json
import sys

from skilz.agents import ExtendedAgentType, get_agent_display_name
from skilz.registry import lookup_skill
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
        registry_skill = lookup_skill(skill.manifest.skill_id, verbose=verbose)

        if skill.manifest.git_sha == registry_skill.git_sha:
            return "up-to-date"
        else:
            return "outdated"

    except Exception:
        # Skill not in registry or registry not found
        return "unknown"


def get_mode_display(skill: InstalledSkill) -> str:
    """
    Get display string for install mode.

    Args:
        skill: The installed skill.

    Returns:
        Mode string with formatting for broken symlinks.
    """
    if skill.is_broken:
        return "[ERROR]"
    if skill.install_mode == "symlink":
        return "[symlink]"
    return "[copy]"


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
    headers = ["Agent", "Skill", "Version", "Mode", "Status"]

    # Build rows
    rows: list[tuple[str, str, str, str, str]] = []
    broken_skills: list[InstalledSkill] = []

    for skill in skills:
        if skill.is_broken:
            status = "broken"
            broken_skills.append(skill)
        else:
            status = get_skill_status(skill, verbose=verbose)

        mode = get_mode_display(skill)
        agent_display = get_agent_display_name(skill.agent)
        rows.append(
            (
                agent_display,
                skill.skill_id,
                skill.git_sha_short,
                mode,
                status,
            )
        )

    # Calculate column widths
    col_widths = [
        max(len(headers[0]), max(len(r[0]) for r in rows)),
        max(len(headers[1]), max(len(r[1]) for r in rows)),
        max(len(headers[2]), max(len(r[2]) for r in rows)),
        max(len(headers[3]), max(len(r[3]) for r in rows)),
        max(len(headers[4]), max(len(r[4]) for r in rows)),
    ]

    # Build output
    lines: list[str] = []

    # Header line
    header_line = "  ".join(h.ljust(col_widths[i]) for i, h in enumerate(headers))
    lines.append(header_line)

    # Separator line
    separator = "\u2500" * (
        sum(col_widths) + 8
    )  # Unicode box drawing char (4 spaces between 5 columns)
    lines.append(separator)

    # Data rows
    for row in rows:
        row_line = "  ".join(val.ljust(col_widths[i]) for i, val in enumerate(row))
        lines.append(row_line)

    # Add broken symlink warnings
    if broken_skills:
        lines.append("")
        lines.append("⚠️  Broken symlinks detected:")
        for skill in broken_skills:
            target = skill.canonical_path or "unknown"
            lines.append(f"   - {skill.skill_id}: target missing ({target})")

    # Summary line with mode counts
    copy_count = sum(1 for s in skills if s.install_mode == "copy" and not s.is_broken)
    symlink_count = sum(1 for s in skills if s.install_mode == "symlink" and not s.is_broken)
    broken_count = len(broken_skills)

    summary_parts = []
    if copy_count:
        summary_parts.append(f"{copy_count} copied")
    if symlink_count:
        summary_parts.append(f"{symlink_count} symlinked")
    if broken_count:
        summary_parts.append(f"{broken_count} broken")

    if summary_parts:
        lines.append("")
        lines.append(f"Total: {len(skills)} skills ({', '.join(summary_parts)})")

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
        if skill.is_broken:
            status = "broken"
        else:
            status = get_skill_status(skill, verbose=verbose)

        skill_data = {
            "skill_id": skill.skill_id,
            "skill_name": skill.skill_name,
            "git_sha": skill.manifest.git_sha,
            "installed_at": skill.manifest.installed_at,
            "status": status,
            "path": str(skill.path),
            "agent": skill.agent,
            "agent_display_name": get_agent_display_name(skill.agent),
            "project_level": skill.project_level,
            "install_mode": skill.install_mode,
            "is_symlink": skill.install_mode == "symlink",
            "is_broken": skill.is_broken,
        }

        if skill.canonical_path:
            skill_data["canonical_path"] = str(skill.canonical_path)

        output.append(skill_data)

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
    agent: ExtendedAgentType | None = getattr(args, "agent", None)
    project_level: bool = getattr(args, "project", False)
    scan_all: bool = getattr(args, "all", False)

    if verbose:
        agent_name = get_agent_display_name(agent) if agent else "all agents"
        level = "project-level" if project_level else "user-level"
        print(f"Scanning for {level} skills in {agent_name}...")

    try:
        skills = scan_installed_skills(
            agent=agent,
            project_level=project_level,
            scan_all=scan_all,
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
