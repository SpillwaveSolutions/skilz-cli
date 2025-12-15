"""Agent detection and path resolution."""

from pathlib import Path
from typing import Literal

AgentType = Literal["claude", "opencode"]

# Default agent paths (used when config module unavailable or as fallback)
DEFAULT_AGENT_PATHS: dict[AgentType, dict[str, Path]] = {
    "claude": {
        "user": Path.home() / ".claude" / "skills",
        "project": Path(".claude") / "skills",
    },
    "opencode": {
        "user": Path.home() / ".config" / "opencode" / "skills",
        "project": Path(".opencode") / "skills",
    },
}

# Backwards compatibility alias
AGENT_PATHS = DEFAULT_AGENT_PATHS


def get_agent_paths() -> dict[AgentType, dict[str, Path]]:
    """
    Get agent paths from configuration.

    Returns paths based on config values, with environment variable overrides.
    Falls back to defaults if config module is unavailable.

    Returns:
        Dictionary mapping agent types to their user/project paths.
    """
    try:
        from skilz.config import get_claude_home, get_opencode_home

        claude_home = get_claude_home()
        opencode_home = get_opencode_home()

        return {
            "claude": {
                "user": claude_home / "skills",
                "project": Path(".claude") / "skills",
            },
            "opencode": {
                "user": opencode_home / "skills",
                "project": Path(".opencode") / "skills",
            },
        }
    except ImportError:
        # Config module not available, use defaults
        return DEFAULT_AGENT_PATHS


def detect_agent(project_dir: Path | None = None) -> AgentType:
    """
    Auto-detect which AI agent is being used.

    Detection order:
    1. Check config file for agent_default setting
    2. Check for .claude/ in project directory or current directory
    3. Check for ~/.claude/ (user has Claude Code installed)
    4. Check for ~/.config/opencode/ (user has OpenCode installed)
    5. Default to "claude" if ambiguous

    Args:
        project_dir: Project directory to check. Uses cwd if None.

    Returns:
        The detected agent type ("claude" or "opencode").
    """
    # Check config for default agent first
    try:
        from skilz.config import get_default_agent

        default_agent = get_default_agent()
        if default_agent is not None:
            return default_agent
    except ImportError:
        pass  # Config module not available

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

    Uses configuration for custom paths, with environment variable overrides.

    Args:
        agent: The agent type ("claude" or "opencode").
        project_level: If True, return project-level path instead of user-level.
        project_dir: Project directory for project-level installs.

    Returns:
        Path to the skills directory.
    """
    agent_paths = get_agent_paths()

    if agent not in agent_paths:
        raise ValueError(f"Unknown agent type: {agent}")

    paths = agent_paths[agent]

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
