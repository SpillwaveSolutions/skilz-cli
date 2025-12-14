"""Agent detection and path resolution."""

from pathlib import Path
from typing import Literal

AgentType = Literal["claude", "opencode"]

# Mapping of agent types to their skills directories
AGENT_PATHS: dict[AgentType, dict[str, Path]] = {
    "claude": {
        "user": Path.home() / ".claude" / "skills",
        "project": Path(".claude") / "skills",
    },
    "opencode": {
        "user": Path.home() / ".config" / "opencode" / "skills",
        "project": Path(".opencode") / "skills",  # Project-level for OpenCode
    },
}


def detect_agent(project_dir: Path | None = None) -> AgentType:
    """
    Auto-detect which AI agent is being used.

    Detection order:
    1. Check for .claude/ in project directory or current directory
    2. Check for ~/.claude/ (user has Claude Code installed)
    3. Check for ~/.config/opencode/ (user has OpenCode installed)
    4. Default to "claude" if ambiguous

    Args:
        project_dir: Project directory to check. Uses cwd if None.

    Returns:
        The detected agent type ("claude" or "opencode").
    """
    project = project_dir or Path.cwd()

    # Check project-level Claude
    if (project / ".claude").exists():
        return "claude"

    # Check user-level Claude
    if (Path.home() / ".claude").exists():
        return "claude"

    # Check user-level OpenCode
    if (Path.home() / ".config" / "opencode").exists():
        return "opencode"

    # Default to Claude
    return "claude"


def get_skills_dir(
    agent: AgentType,
    project_level: bool = False,
    project_dir: Path | None = None,
) -> Path:
    """
    Get the skills directory for a given agent.

    Args:
        agent: The agent type ("claude" or "opencode").
        project_level: If True, return project-level path instead of user-level.
        project_dir: Project directory for project-level installs.

    Returns:
        Path to the skills directory.
    """
    if agent not in AGENT_PATHS:
        raise ValueError(f"Unknown agent type: {agent}")

    paths = AGENT_PATHS[agent]

    if project_level:
        project = project_dir or Path.cwd()
        # Return absolute path for project-level
        return (project / paths["project"]).resolve()
    else:
        return paths["user"]


def ensure_skills_dir(
    agent: AgentType,
    project_level: bool = False,
    project_dir: Path | None = None,
) -> Path:
    """
    Get the skills directory, creating it if it doesn't exist.

    Args:
        agent: The agent type ("claude" or "opencode").
        project_level: If True, use project-level path.
        project_dir: Project directory for project-level installs.

    Returns:
        Path to the skills directory (guaranteed to exist).
    """
    skills_dir = get_skills_dir(agent, project_level, project_dir)
    skills_dir.mkdir(parents=True, exist_ok=True)
    return skills_dir


def get_agent_display_name(agent: AgentType) -> str:
    """Get a human-readable name for the agent."""
    names = {
        "claude": "Claude Code",
        "opencode": "OpenCode",
    }
    return names.get(agent, agent)
