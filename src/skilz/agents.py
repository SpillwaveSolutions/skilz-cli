"""Agent detection and path resolution.

This module provides backward-compatible functions for agent detection
and path resolution. It delegates to the agent_registry module for the
actual agent configurations.

Supports 30+ AI coding assistants following the agentskills.io standard.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import TYPE_CHECKING, Literal

if TYPE_CHECKING:
    from skilz.agent_registry import AgentConfig

logger = logging.getLogger(__name__)

# Backward-compatible AgentType (original two agents)
# New code should use get_all_agent_types() or agent_registry directly
AgentType = Literal["claude", "opencode"]

# Extended agent type including all supported agents
ExtendedAgentType = Literal[
    # Original agents
    "claude",
    "opencode",
    "codex",
    "gemini",
    "copilot",
    "aider",
    "cursor",
    "windsurf",
    "qwen",
    "crush",
    "kimi",
    "plandex",
    "zed",
    "universal",
    # New agents (Issues #46, #47, #49)
    "antigravity",
    "openhands",
    "cline",
    "goose",
    "roo",
    "kilo",
    "trae",
    "droid",
    "clawdbot",
    "kiro-cli",
    "pi",
    "neovate",
    "zencoder",
    "amp",
    "qoder",
    "command-code",
]

# Default agent paths (used as fallback when registry unavailable)
DEFAULT_AGENT_PATHS: dict[str, dict[str, Path]] = {
    "claude": {
        "user": Path.home() / ".claude" / "skills",
        "project": Path(".claude") / "skills",
    },
    "opencode": {
        "user": Path.home() / ".config" / "opencode" / "skill",  # singular
        "project": Path(".opencode") / "skill",  # singular
    },
}

# Backwards compatibility alias
AGENT_PATHS = DEFAULT_AGENT_PATHS


def get_all_agent_types() -> list[str]:
    """Get all registered agent type names.

    Returns:
        List of all agent identifiers from the registry.
    """
    try:
        from skilz.agent_registry import get_registry

        return get_registry().list_agents()
    except ImportError:
        return list(DEFAULT_AGENT_PATHS.keys())


def get_agent_paths() -> dict[str, dict[str, Path]]:
    """
    Get agent paths from the registry with config overrides.

    Returns paths for all registered agents, applying configuration
    overrides from environment variables (CLAUDE_CODE_HOME, OPEN_CODE_HOME)
    and config file settings.

    Returns:
        Dictionary mapping agent types to their user/project paths.
    """
    # Get config overrides first (for backward compatibility)
    claude_home: Path | None = None
    opencode_home: Path | None = None

    try:
        from skilz.config import get_claude_home, get_opencode_home

        claude_home = get_claude_home()
        opencode_home = get_opencode_home()
    except ImportError:
        pass

    try:
        from skilz.agent_registry import get_registry

        registry = get_registry()
        result: dict[str, dict[str, Path]] = {}

        for name in registry.list_agents():
            agent = registry.get(name)
            if agent is None:
                continue

            paths: dict[str, Path] = {"project": agent.project_dir}
            if agent.supports_home and agent.home_dir:
                # Apply config overrides for claude and opencode
                if name == "claude" and claude_home:
                    paths["user"] = claude_home / "skills"
                elif name == "opencode" and opencode_home:
                    paths["user"] = opencode_home / "skill"  # singular
                else:
                    paths["user"] = agent.home_dir

            result[name] = paths

        return result
    except ImportError:
        # Registry module not available, use defaults with config overrides
        result = dict(DEFAULT_AGENT_PATHS)
        if claude_home:
            result["claude"]["user"] = claude_home / "skills"
        if opencode_home:
            result["opencode"]["user"] = opencode_home / "skill"  # singular
        return result


def _check_parent_skilz(project_dir: Path) -> str | None:
    """Check for ../skilz/skills directory (universal agent pattern).

    Args:
        project_dir: The project directory to check from.

    Returns:
        "universal" if parent skilz/skills exists, None otherwise.
    """
    parent = project_dir.parent
    parent_skilz = parent / "skilz" / "skills"
    if parent_skilz.exists() and parent_skilz.is_dir():
        logger.debug("[SKILZ-081] Found parent skilz/skills at %s", parent_skilz)
        return "universal"
    return None


def detect_agent(project_dir: Path | None = None) -> str:
    """
    Auto-detect which AI agent is being used.

    Detection order:
    1. Check config file for agent_default setting
    2. Check for ../skilz/skills (parent directory universal pattern)
    3. Check for .claude/ in project directory
    4. Check for .gemini/ in project directory (Gemini CLI native skills)
    5. Check for .codex/ in project directory (OpenAI Codex native skills)
    6. Check for ~/.claude/ (user has Claude Code installed)
    7. Check for ~/.gemini/ (user has Gemini CLI native skills)
    8. Check for ~/.codex/ (user has OpenAI Codex installed)
    9. Check for ~/.config/opencode/ (user has OpenCode installed)
    10. Default to "claude" if ambiguous

    Args:
        project_dir: Project directory to check. Uses cwd if None.

    Returns:
        The detected agent type (e.g., "claude", "opencode", "gemini", "codex").
    """
    # Check config for default agent first
    try:
        from skilz.config import get_default_agent

        default_agent = get_default_agent()
        if default_agent:
            return default_agent
    except ImportError:
        pass  # Config module not available

    project = project_dir or Path.cwd()

    # SKILZ-081: Check parent directory for universal agent pattern
    parent_agent = _check_parent_skilz(project)
    if parent_agent:
        return parent_agent

    # Check project-level markers (highest priority)
    # Order by popularity/usage from Issue #49 table
    if (project / ".gemini").exists():
        return "gemini"

    if (project / ".opencode").exists():
        return "opencode"

    if (project / ".openhands").exists():
        return "openhands"

    if (project / ".claude").exists():
        return "claude"

    if (project / ".cline").exists():
        return "cline"

    if (project / ".codex").exists():
        return "codex"

    if (project / ".cursor").exists():
        return "cursor"

    if (project / ".goose").exists():
        return "goose"

    if (project / ".roo").exists():
        return "roo"

    if (project / ".kilocode").exists():
        return "kilo"

    if (project / ".trae").exists():
        return "trae"

    if (project / ".factory").exists():
        return "droid"

    if (project / ".kiro").exists():
        return "kiro-cli"

    if (project / ".pi").exists():
        return "pi"

    if (project / ".neovate").exists():
        return "neovate"

    if (project / ".agent").exists():
        return "antigravity"

    if (project / ".windsurf").exists():
        return "windsurf"

    if (project / ".github").exists():
        return "copilot"

    if (project / ".qwen").exists():
        return "qwen"

    if (project / ".zencoder").exists():
        return "zencoder"

    if (project / ".agents").exists():
        return "amp"

    if (project / ".qoder").exists():
        return "qoder"

    if (project / ".commandcode").exists():
        return "command-code"

    # Special case: Clawdbot uses skills/ at project root
    if (project / "skills").exists() and (project / "skills").is_dir():
        # Check if it looks like a Clawdbot skills dir
        skills_dir = project / "skills"
        if any((skills_dir / d / "SKILL.md").exists() for d in skills_dir.iterdir() if d.is_dir()):
            return "clawdbot"

    # Check user-level markers (use Path.home() at detection time, not cached)
    if (Path.home() / ".claude").exists():
        return "claude"

    if (Path.home() / ".gemini").exists():
        return "gemini"

    if (Path.home() / ".codex").exists():
        return "codex"

    # Check user-level OpenCode
    if (Path.home() / ".config" / "opencode").exists():
        return "opencode"

    # Check other project-level agent directories
    try:
        from skilz.agent_registry import get_registry

        registry = get_registry()

        # Check less common agents
        for agent_name in registry.list_agents():
            if agent_name in ("claude", "opencode", "gemini", "codex"):
                continue  # Already checked above
            agent = registry.get(agent_name)
            if agent:
                project_marker = agent.project_dir.parts[0] if agent.project_dir.parts else None
                if project_marker and (project / project_marker).exists():
                    return agent_name

    except ImportError:
        pass

    # SKILZ-085: Default to Claude
    logger.debug("[SKILZ-085] No agent markers found, using default: claude")
    return "claude"


def get_skills_dir(
    agent: str,
    project_level: bool = False,
    project_dir: Path | None = None,
) -> Path:
    """
    Get the skills directory for a given agent.

    Uses registry configuration for paths, with user overrides from
    environment variables (CLAUDE_CODE_HOME, OPEN_CODE_HOME) and config file.

    Args:
        agent: The agent type (e.g., "claude", "opencode", "gemini").
        project_level: If True, return project-level path instead of user-level.
        project_dir: Project directory for project-level installs.

    Returns:
        Path to the skills directory.

    Raises:
        ValueError: If agent is unknown or doesn't support the requested level.
    """
    # For user-level, use get_agent_paths() which applies config overrides
    if not project_level:
        agent_paths = get_agent_paths()

        if agent not in agent_paths:
            raise ValueError(f"Unknown agent type: {agent}")

        paths = agent_paths[agent]

        if "user" not in paths:
            raise ValueError(
                f"Agent '{agent}' does not support user-level installation. "
                "Use --project flag for project-level installation."
            )
        return paths["user"]

    # For project-level, use registry directly
    try:
        from skilz.agent_registry import get_registry

        registry = get_registry()
        agent_config = registry.get(agent)

        if agent_config is None:
            raise ValueError(f"Unknown agent type: {agent}")

        project = project_dir or Path.cwd()
        return (project / agent_config.project_dir).resolve()

    except ImportError:
        # Fallback to old behavior
        if agent not in DEFAULT_AGENT_PATHS:
            raise ValueError(f"Unknown agent type: {agent}")

        project = project_dir or Path.cwd()
        return (project / DEFAULT_AGENT_PATHS[agent]["project"]).resolve()


def ensure_skills_dir(
    agent: str,
    project_level: bool = False,
    project_dir: Path | None = None,
) -> Path:
    """
    Get the skills directory, creating it if it doesn't exist.

    Args:
        agent: The agent type (e.g., "claude", "opencode", "gemini").
        project_level: If True, use project-level path.
        project_dir: Project directory for project-level installs.

    Returns:
        Path to the skills directory (guaranteed to exist).
    """
    skills_dir = get_skills_dir(agent, project_level, project_dir)
    skills_dir.mkdir(parents=True, exist_ok=True)
    return skills_dir


def get_agent_display_name(agent: str) -> str:
    """Get a human-readable name for the agent.

    Args:
        agent: The agent identifier

    Returns:
        Human-readable display name
    """
    try:
        from skilz.agent_registry import get_registry

        agent_config = get_registry().get(agent)
        if agent_config:
            return agent_config.display_name
    except ImportError:
        pass

    # Fallback for known agents
    names = {
        "claude": "Claude Code",
        "opencode": "OpenCode",
    }
    return names.get(agent, agent)


def get_agent_config(agent: str) -> AgentConfig | None:
    """Get the full AgentConfig for an agent.

    Args:
        agent: The agent identifier

    Returns:
        AgentConfig or None if not found

    Note:
        Returns None instead of raising to allow graceful degradation.
    """
    try:
        from skilz.agent_registry import get_registry

        return get_registry().get(agent)
    except ImportError:
        return None


def get_agent_default_mode(agent: str) -> str:
    """Get the default installation mode for an agent.

    Args:
        agent: The agent identifier

    Returns:
        "copy" or "symlink"
    """
    try:
        from skilz.agent_registry import get_registry

        agent_config = get_registry().get(agent)
        if agent_config:
            return agent_config.default_mode
    except ImportError:
        pass

    # Claude uses copy by default, others use symlink
    return "copy" if agent == "claude" else "symlink"


def supports_home_install(agent: str) -> bool:
    """Check if an agent supports user-level installation.

    Args:
        agent: The agent identifier

    Returns:
        True if agent supports home directory installation
    """
    try:
        from skilz.agent_registry import get_registry

        agent_config = get_registry().get(agent)
        if agent_config:
            return agent_config.supports_home
    except ImportError:
        pass

    # Fallback: only claude and opencode support home
    return agent in ("claude", "opencode", "codex", "universal")
