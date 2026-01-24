"""Agent registry for multi-agent CLI support.

This module provides a configurable registry of AI coding assistants,
enabling support for 30+ agents following the agentskills.io open standard.

The registry can be customized via ~/.config/skilz/config.json.
"""

from __future__ import annotations

import json
import re
import unicodedata
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Literal, cast

# Validation constants (from agentskills.io spec)
MAX_SKILL_NAME_LENGTH = 64
MAX_DESCRIPTION_LENGTH = 1024
SKILL_NAME_PATTERN = re.compile(r"^[a-z][a-z0-9]*(-[a-z0-9]+)*$")


@dataclass(frozen=True)
class AgentConfig:
    """Configuration for an AI coding assistant agent.

    This is an immutable dataclass representing an agent's configuration.
    All paths are expanded (~ resolved) at creation time.

    Attributes:
        name: Internal identifier (e.g., "claude", "gemini")
        display_name: Human-readable name (e.g., "Claude Code", "Gemini CLI")
        home_dir: User-level skills path (e.g., ~/.claude/skills), None if not supported
        project_dir: Project-level skills path (e.g., .claude/skills)
        config_files: Files to sync skill metadata (e.g., ("GEMINI.md",))
        supports_home: Whether agent supports user-level installation
        default_mode: "copy" or "symlink" for installation
        native_skill_support: "all", "home", or "none"
        uses_folder_rules: Whether agent uses folder-based rules (like Cursor)
        invocation: How skills are invoked (documentation only)
    """

    name: str
    display_name: str
    home_dir: Path | None
    project_dir: Path
    config_files: tuple[str, ...]
    supports_home: bool
    default_mode: Literal["copy", "symlink"]
    native_skill_support: Literal["all", "home", "none"]
    uses_folder_rules: bool = False
    invocation: str | None = None

    @classmethod
    def from_dict(cls, name: str, data: dict[str, Any]) -> AgentConfig:
        """Create AgentConfig from a dictionary (JSON parsing).

        Args:
            name: The agent identifier
            data: Dictionary with agent configuration

        Returns:
            AgentConfig instance

        Raises:
            ValueError: If required fields are missing or invalid
        """
        # Required fields
        required = ["display_name", "project_dir", "default_mode"]
        for field_name in required:
            if field_name not in data:
                raise ValueError(f"Missing required field '{field_name}' for agent '{name}'")

        # Validate default_mode
        default_mode = data["default_mode"]
        if default_mode not in ("copy", "symlink"):
            raise ValueError(
                f"Invalid default_mode '{default_mode}' for agent '{name}'. "
                "Must be 'copy' or 'symlink'"
            )

        # Validate native_skill_support
        native_support = data.get("native_skill_support", "none")
        if native_support not in ("all", "home", "none"):
            raise ValueError(
                f"Invalid native_skill_support '{native_support}' for agent '{name}'. "
                "Must be 'all', 'home', or 'none'"
            )

        # Parse home_dir (expand ~)
        home_dir = None
        if "home_dir" in data and data["home_dir"]:
            home_dir = Path(data["home_dir"]).expanduser()

        # Parse project_dir
        project_dir = Path(data["project_dir"])

        # Parse config_files as tuple
        config_files = tuple(data.get("config_files", []))

        return cls(
            name=name,
            display_name=data["display_name"],
            home_dir=home_dir,
            project_dir=project_dir,
            config_files=config_files,
            supports_home=data.get("supports_home", False),
            default_mode=default_mode,
            native_skill_support=native_support,
            uses_folder_rules=data.get("uses_folder_rules", False),
            invocation=data.get("invocation"),
        )


def _create_builtin_agents() -> dict[str, AgentConfig]:
    """Create the built-in agent definitions."""
    return {
        "claude": AgentConfig(
            name="claude",
            display_name="Claude Code",
            home_dir=Path.home() / ".claude" / "skills",
            project_dir=Path(".claude") / "skills",
            config_files=("CLAUDE.md",),
            supports_home=True,
            default_mode="copy",
            native_skill_support="all",
        ),
        "opencode": AgentConfig(
            name="opencode",
            display_name="OpenCode CLI",
            home_dir=Path.home() / ".config" / "opencode" / "skill",  # singular
            project_dir=Path(".opencode") / "skill",  # singular
            config_files=("AGENTS.md",),
            supports_home=True,
            default_mode="copy",
            native_skill_support="all",  # OpenCode reads skills natively
        ),
        "codex": AgentConfig(
            name="codex",
            display_name="OpenAI Codex",
            home_dir=Path.home() / ".codex" / "skills",
            project_dir=Path(".codex") / "skills",
            config_files=("AGENTS.md",),
            supports_home=True,
            default_mode="copy",
            native_skill_support="all",
            invocation="$skill-name or /skills",
        ),
        "gemini": AgentConfig(
            name="gemini",
            display_name="Gemini CLI",
            home_dir=Path.home() / ".gemini" / "skills",
            project_dir=Path(".gemini") / "skills",
            config_files=("GEMINI.md",),
            supports_home=True,
            default_mode="copy",
            native_skill_support="all",
            invocation="/skills or activate_skill tool",
        ),
        "copilot": AgentConfig(
            name="copilot",
            display_name="GitHub Copilot",
            home_dir=Path.home() / ".copilot" / "skills",  # Added global support
            project_dir=Path(".github") / "skills",  # Copilot native skills dir
            config_files=(".github/copilot-instructions.md",),
            supports_home=True,  # Changed from False
            default_mode="copy",
            native_skill_support="all",  # Copilot reads .github/skills/ natively
        ),
        "aider": AgentConfig(
            name="aider",
            display_name="Aider",
            home_dir=None,
            project_dir=Path(".skilz") / "skills",
            config_files=("CONVENTIONS.md",),
            supports_home=False,
            default_mode="copy",
            native_skill_support="none",
        ),
        "cursor": AgentConfig(
            name="cursor",
            display_name="Cursor",
            home_dir=Path.home() / ".cursor" / "skills",  # Added global support
            project_dir=Path(".cursor") / "skills",  # Changed from .skilz
            config_files=(".cursor/rules/RULES.md", ".cursor/rules/RULE.md"),
            supports_home=True,  # Changed from False
            default_mode="copy",
            native_skill_support="all",  # Changed from none
            uses_folder_rules=True,
        ),
        "windsurf": AgentConfig(
            name="windsurf",
            display_name="Windsurf",
            home_dir=Path.home() / ".codeium" / "windsurf" / "skills",  # Added global support
            project_dir=Path(".windsurf") / "skills",  # Changed from .skilz
            config_files=("AGENTS.md",),  # Added config file
            supports_home=True,  # Changed from False
            default_mode="copy",
            native_skill_support="all",  # Changed from none
        ),
        "qwen": AgentConfig(
            name="qwen",
            display_name="Qwen Code",
            home_dir=Path.home() / ".qwen" / "skills",  # Added global support
            project_dir=Path(".qwen") / "skills",  # Changed from .skilz
            config_files=("QWEN.md",),  # Simplified config files
            supports_home=True,  # Changed from False
            default_mode="copy",
            native_skill_support="all",  # Changed from none - Issue #46
        ),
        "crush": AgentConfig(
            name="crush",
            display_name="Crush",
            home_dir=None,
            project_dir=Path(".skilz") / "skills",
            config_files=(),
            supports_home=False,
            default_mode="copy",
            native_skill_support="none",
        ),
        "kimi": AgentConfig(
            name="kimi",
            display_name="Kimi CLI",
            home_dir=None,
            project_dir=Path(".skilz") / "skills",
            config_files=(),
            supports_home=False,
            default_mode="copy",
            native_skill_support="none",
        ),
        "plandex": AgentConfig(
            name="plandex",
            display_name="Plandex",
            home_dir=None,
            project_dir=Path(".skilz") / "skills",
            config_files=(),
            supports_home=False,
            default_mode="copy",
            native_skill_support="none",
        ),
        "zed": AgentConfig(
            name="zed",
            display_name="Zed AI",
            home_dir=None,
            project_dir=Path(".skilz") / "skills",
            config_files=(),
            supports_home=False,
            default_mode="copy",
            native_skill_support="none",
        ),
        # NEW AGENTS (Issues #46, #47, #49)
        "antigravity": AgentConfig(
            name="antigravity",
            display_name="Google Antigravity",
            home_dir=Path.home() / ".gemini" / "antigravity" / "skills",
            project_dir=Path(".agent") / "skills",
            config_files=(),  # Native discovery
            supports_home=True,
            default_mode="copy",
            native_skill_support="all",
        ),
        "openhands": AgentConfig(
            name="openhands",
            display_name="OpenHands",
            home_dir=Path.home() / ".openhands" / "skills",
            project_dir=Path(".openhands") / "skills",
            config_files=("AGENTS.md",),
            supports_home=True,
            default_mode="copy",
            native_skill_support="all",
        ),
        "cline": AgentConfig(
            name="cline",
            display_name="Cline",
            home_dir=Path.home() / ".cline" / "skills",
            project_dir=Path(".cline") / "skills",
            config_files=("AGENTS.md",),
            supports_home=True,
            default_mode="copy",
            native_skill_support="all",
        ),
        "goose": AgentConfig(
            name="goose",
            display_name="Goose",
            home_dir=Path.home() / ".config" / "goose" / "skills",
            project_dir=Path(".goose") / "skills",
            config_files=("AGENTS.md",),
            supports_home=True,
            default_mode="copy",
            native_skill_support="all",
        ),
        "roo": AgentConfig(
            name="roo",
            display_name="Roo Code",
            home_dir=Path.home() / ".roo" / "skills",
            project_dir=Path(".roo") / "skills",
            config_files=("AGENTS.md",),
            supports_home=True,
            default_mode="copy",
            native_skill_support="all",
        ),
        "kilo": AgentConfig(
            name="kilo",
            display_name="Kilo Code",
            home_dir=Path.home() / ".kilocode" / "skills",
            project_dir=Path(".kilocode") / "skills",
            config_files=("AGENTS.md",),
            supports_home=True,
            default_mode="copy",
            native_skill_support="all",
        ),
        "trae": AgentConfig(
            name="trae",
            display_name="Trae",
            home_dir=Path.home() / ".trae" / "skills",
            project_dir=Path(".trae") / "skills",
            config_files=("AGENTS.md",),
            supports_home=True,
            default_mode="copy",
            native_skill_support="all",
        ),
        "droid": AgentConfig(
            name="droid",
            display_name="Droid",
            home_dir=Path.home() / ".factory" / "skills",
            project_dir=Path(".factory") / "skills",
            config_files=("AGENTS.md",),
            supports_home=True,
            default_mode="copy",
            native_skill_support="all",
        ),
        "clawdbot": AgentConfig(
            name="clawdbot",
            display_name="Clawdbot",
            home_dir=Path.home() / ".clawdbot" / "skills",
            project_dir=Path("skills"),  # Unique: project root skills/
            config_files=("AGENTS.md",),
            supports_home=True,
            default_mode="copy",
            native_skill_support="all",
        ),
        "kiro-cli": AgentConfig(
            name="kiro-cli",
            display_name="Kiro CLI",
            home_dir=Path.home() / ".kiro" / "skills",
            project_dir=Path(".kiro") / "skills",
            config_files=("AGENTS.md",),
            supports_home=True,
            default_mode="copy",
            native_skill_support="all",
        ),
        "pi": AgentConfig(
            name="pi",
            display_name="Pi",
            home_dir=Path.home() / ".pi" / "agent" / "skills",
            project_dir=Path(".pi") / "skills",
            config_files=("AGENTS.md",),
            supports_home=True,
            default_mode="copy",
            native_skill_support="all",
        ),
        "neovate": AgentConfig(
            name="neovate",
            display_name="Neovate",
            home_dir=Path.home() / ".neovate" / "skills",
            project_dir=Path(".neovate") / "skills",
            config_files=("AGENTS.md",),
            supports_home=True,
            default_mode="copy",
            native_skill_support="all",
        ),
        "zencoder": AgentConfig(
            name="zencoder",
            display_name="Zencoder",
            home_dir=Path.home() / ".zencoder" / "skills",
            project_dir=Path(".zencoder") / "skills",
            config_files=("AGENTS.md",),
            supports_home=True,
            default_mode="copy",
            native_skill_support="all",
        ),
        "amp": AgentConfig(
            name="amp",
            display_name="Amp",
            home_dir=Path.home() / ".config" / "agents" / "skills",
            project_dir=Path(".agents") / "skills",
            config_files=("AGENTS.md",),
            supports_home=True,
            default_mode="copy",
            native_skill_support="all",
        ),
        "qoder": AgentConfig(
            name="qoder",
            display_name="Qoder",
            home_dir=Path.home() / ".qoder" / "skills",
            project_dir=Path(".qoder") / "skills",
            config_files=("AGENTS.md",),
            supports_home=True,
            default_mode="copy",
            native_skill_support="all",
        ),
        "command-code": AgentConfig(
            name="command-code",
            display_name="Command Code",
            home_dir=Path.home() / ".commandcode" / "skills",
            project_dir=Path(".commandcode") / "skills",
            config_files=("AGENTS.md",),
            supports_home=True,
            default_mode="copy",
            native_skill_support="all",
        ),
        "universal": AgentConfig(
            name="universal",
            display_name="Universal (Skilz)",
            home_dir=Path.home() / ".skilz" / "skills",
            project_dir=Path(".skilz") / "skills",
            config_files=("AGENTS.md",),  # SKILZ-50: Enable project-level config sync
            supports_home=True,
            default_mode="copy",
            native_skill_support="none",
        ),
    }


# Built-in agents (created lazily to avoid import-time side effects)
_BUILTIN_AGENTS: dict[str, AgentConfig] | None = None


def get_builtin_agents() -> dict[str, AgentConfig]:
    """Get the built-in agent definitions."""
    global _BUILTIN_AGENTS
    if _BUILTIN_AGENTS is None:
        _BUILTIN_AGENTS = _create_builtin_agents()
    return _BUILTIN_AGENTS


# Default skills directory (used as symlink source for project-level installs)
DEFAULT_SKILLS_DIR = Path.home() / ".claude" / "skills"


@dataclass
class SkillNameValidation:
    """Result of skill name validation.

    Attributes:
        is_valid: Whether the name is valid
        normalized_name: The normalized name (NFKC, lowercase)
        errors: List of validation errors
        suggested_name: Suggested corrected name if invalid
    """

    is_valid: bool
    normalized_name: str
    errors: list[str] = field(default_factory=list)
    suggested_name: str | None = None


def validate_skill_name(name: str) -> SkillNameValidation:
    """Validate a skill name according to agentskills.io spec.

    Rules:
    - Lowercase only
    - Letters, digits, hyphens only
    - No leading/trailing hyphens
    - No consecutive hyphens
    - NFKC Unicode normalization
    - Max 64 characters

    Args:
        name: The skill name to validate

    Returns:
        SkillNameValidation with results
    """
    errors: list[str] = []

    # NFKC normalization for i18n support
    normalized = unicodedata.normalize("NFKC", name).lower()

    # Check length
    if len(normalized) > MAX_SKILL_NAME_LENGTH:
        errors.append(f"Name exceeds {MAX_SKILL_NAME_LENGTH} characters")

    # Check empty
    if not normalized:
        errors.append("Name cannot be empty")
        return SkillNameValidation(
            is_valid=False,
            normalized_name=normalized,
            errors=errors,
        )

    # Check pattern
    if not SKILL_NAME_PATTERN.match(normalized):
        errors.append(
            "Name must be lowercase letters, digits, and hyphens only. "
            "Must start with a letter. No consecutive or trailing hyphens."
        )

    # Generate suggested name if invalid
    suggested = None
    if errors:
        # Try to create a valid name
        suggested = _suggest_valid_name(normalized)

    return SkillNameValidation(
        is_valid=len(errors) == 0,
        normalized_name=normalized,
        errors=errors,
        suggested_name=suggested,
    )


def _suggest_valid_name(name: str) -> str:
    """Suggest a valid skill name from an invalid one.

    Args:
        name: The invalid name

    Returns:
        A suggested valid name
    """
    # Remove invalid characters, replace spaces/underscores with hyphens
    result = name.lower()
    result = re.sub(r"[_\s]+", "-", result)
    result = re.sub(r"[^a-z0-9-]", "", result)

    # Remove consecutive hyphens
    result = re.sub(r"-+", "-", result)

    # Remove leading/trailing hyphens
    result = result.strip("-")

    # Ensure starts with letter
    if result and not result[0].isalpha():
        result = "skill-" + result

    # Truncate if needed
    if len(result) > MAX_SKILL_NAME_LENGTH:
        result = result[:MAX_SKILL_NAME_LENGTH].rstrip("-")

    return result or "skill"


def check_skill_directory_name(skill_dir: Path, expected_name: str) -> tuple[bool, str | None]:
    """Check if a skill directory name matches the expected skill name.

    Args:
        skill_dir: Path to the skill directory
        expected_name: Expected skill name (from SKILL.md frontmatter)

    Returns:
        Tuple of (matches, suggested_new_path) where suggested_new_path is
        the path to rename to if names don't match, or None if they match.
    """
    dir_name = skill_dir.name
    validation = validate_skill_name(expected_name)

    if not validation.is_valid:
        # Use suggested name if the expected name is invalid
        target_name = validation.suggested_name or expected_name
    else:
        target_name = validation.normalized_name

    if dir_name == target_name:
        return True, None

    # Names don't match - suggest rename
    new_path = skill_dir.parent / target_name
    return False, str(new_path)


def rename_skill_directory(skill_dir: Path, new_name: str) -> Path:
    """Rename a skill directory to match its skill name.

    Args:
        skill_dir: Current path to the skill directory
        new_name: New directory name

    Returns:
        Path to the renamed directory

    Raises:
        FileExistsError: If target directory already exists
        OSError: If rename fails
    """
    new_path = skill_dir.parent / new_name

    if new_path.exists():
        raise FileExistsError(f"Cannot rename: '{new_path}' already exists")

    skill_dir.rename(new_path)
    return new_path


class AgentRegistry:
    """Registry of AI coding assistant agents.

    Manages agent configurations with support for user customization
    via ~/.config/skilz/config.json.

    The registry merges user configuration on top of built-in defaults,
    allowing users to override or add agents without code changes.
    """

    def __init__(self, config_path: Path | None = None) -> None:
        """Initialize the agent registry.

        Args:
            config_path: Path to user config file. If None, uses default location.
        """
        self._agents: dict[str, AgentConfig] = {}
        self._default_skills_dir: Path = DEFAULT_SKILLS_DIR
        self._load(config_path)

    def _load(self, config_path: Path | None) -> None:
        """Load agent configurations.

        Args:
            config_path: Path to user config file, or None for defaults only.
        """
        # Start with built-in defaults
        self._agents = dict(get_builtin_agents())

        # Try to load user config
        if config_path is None:
            config_path = self._get_default_config_path()

        if config_path and config_path.exists():
            user_config = self._load_user_config(config_path)
            if user_config:
                self._merge_user_config(user_config)

    def _get_default_config_path(self) -> Path:
        """Get the default config file path."""
        return Path.home() / ".config" / "skilz" / "config.json"

    def _load_user_config(self, config_path: Path) -> dict[str, Any] | None:
        """Load user configuration from file.

        Args:
            config_path: Path to the config file

        Returns:
            Parsed config dictionary, or None if loading fails
        """
        try:
            with open(config_path) as f:
                return cast(dict[str, Any], json.load(f))
        except (json.JSONDecodeError, OSError):
            # Corrupted or unreadable file - use defaults
            return None

    def _merge_user_config(self, user_config: dict[str, Any]) -> None:
        """Merge user configuration with built-in defaults.

        Args:
            user_config: User configuration dictionary
        """
        # Update default_skills_dir if specified
        if "default_skills_dir" in user_config:
            self._default_skills_dir = Path(user_config["default_skills_dir"]).expanduser()

        # Merge agents
        if "agents" in user_config:
            for name, agent_data in user_config["agents"].items():
                try:
                    agent_config = AgentConfig.from_dict(name, agent_data)
                    self._agents[name] = agent_config
                except (ValueError, KeyError):
                    # Invalid agent config - skip it
                    pass

    def get(self, name: str) -> AgentConfig | None:
        """Get agent configuration by name.

        Args:
            name: Agent identifier (e.g., "claude", "gemini")

        Returns:
            AgentConfig if found, None otherwise
        """
        return self._agents.get(name)

    def get_or_raise(self, name: str) -> AgentConfig:
        """Get agent configuration by name, raising if not found.

        Args:
            name: Agent identifier

        Returns:
            AgentConfig

        Raises:
            ValueError: If agent not found
        """
        agent = self._agents.get(name)
        if agent is None:
            valid_agents = ", ".join(sorted(self._agents.keys()))
            raise ValueError(f"Unknown agent: '{name}'. Valid agents: {valid_agents}")
        return agent

    def list_agents(self) -> list[str]:
        """Get list of all registered agent names.

        Returns:
            Sorted list of agent identifiers
        """
        return sorted(self._agents.keys())

    def get_default_skills_dir(self) -> Path:
        """Get the default skills directory for symlink sources.

        Returns:
            Path to default skills directory (usually ~/.claude/skills)
        """
        return self._default_skills_dir

    def get_agents_with_home_support(self) -> list[str]:
        """Get agents that support user-level installation.

        Returns:
            List of agent names with supports_home=True
        """
        return [name for name, agent in self._agents.items() if agent.supports_home]

    def get_agents_by_native_support(self, level: Literal["all", "home", "none"]) -> list[str]:
        """Get agents by their native skill support level.

        Args:
            level: The native_skill_support level to filter by

        Returns:
            List of agent names with the specified support level
        """
        return [name for name, agent in self._agents.items() if agent.native_skill_support == level]


# Module-level singleton
_registry: AgentRegistry | None = None


def get_registry() -> AgentRegistry:
    """Get the global agent registry singleton.

    Returns:
        The AgentRegistry instance
    """
    global _registry
    if _registry is None:
        _registry = AgentRegistry()
    return _registry


def reset_registry() -> None:
    """Reset the global registry singleton.

    Useful for testing when you need to reload configuration.
    """
    global _registry
    _registry = None


def get_agent_choices() -> list[str]:
    """Get list of valid agent names for CLI choices.

    Returns:
        Sorted list of agent identifiers

    Note:
        Falls back to ["claude", "opencode"] if registry fails.
    """
    try:
        return get_registry().list_agents()
    except Exception:
        return ["claude", "opencode"]
