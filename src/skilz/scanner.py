"""Scanner for discovering installed skills."""

from dataclasses import dataclass
from pathlib import Path
from typing import cast

from skilz.agent_registry import get_registry
from skilz.agents import ExtendedAgentType, get_skills_dir
from skilz.link_ops import get_symlink_target, is_broken_symlink, is_symlink
from skilz.manifest import InstallMode, SkillManifest, read_manifest

# Top agents to scan by default (covers 99% of users)
TOP_AGENTS = ["claude", "opencode", "gemini", "codex", "copilot"]


@dataclass
class InstalledSkill:
    """Represents an installed skill with its metadata."""

    skill_id: str
    skill_name: str
    path: Path
    manifest: SkillManifest
    agent: ExtendedAgentType
    project_level: bool
    install_mode: InstallMode = "copy"
    canonical_path: Path | None = None
    is_broken: bool = False

    @property
    def git_sha_short(self) -> str:
        """Return first 8 characters of git SHA."""
        return self.manifest.git_sha[:8] if self.manifest.git_sha else ""

    @property
    def installed_at_short(self) -> str:
        """Return just the date portion of installed_at."""
        # installed_at is ISO format like "2025-01-15T14:32:00+00:00"
        if self.manifest.installed_at:
            return self.manifest.installed_at[:10]
        return ""

    def to_dict(self) -> dict:
        """Convert to dictionary for serialization."""
        return {
            "skill_id": self.skill_id,
            "skill_name": self.skill_name,
            "path": str(self.path),
            "agent": self.agent,
            "project_level": self.project_level,
            "install_mode": self.install_mode,
            "canonical_path": str(self.canonical_path) if self.canonical_path else None,
            "is_broken": self.is_broken,
        }


def scan_skills_directory(
    skills_dir: Path,
    agent: ExtendedAgentType,
    project_level: bool,
) -> list[InstalledSkill]:
    """
    Scan a skills directory for installed skills with manifests.

    Handles both regular directories and symlinks. For symlinked skills,
    reads the manifest from the canonical (target) location and tracks
    the symlink status. Broken symlinks are detected and reported.

    Args:
        skills_dir: Path to the skills directory to scan.
        agent: The agent type this directory belongs to.
        project_level: Whether this is a project-level installation.

    Returns:
        List of InstalledSkill objects found in the directory.
    """
    installed: list[InstalledSkill] = []

    if not skills_dir.exists():
        return installed

    # Iterate over subdirectories in the skills directory
    try:
        for skill_dir in skills_dir.iterdir():
            # Check for broken symlink first (before is_dir check)
            if is_broken_symlink(skill_dir):
                # Create a placeholder for broken symlinks
                canonical = get_symlink_target(skill_dir)
                installed.append(
                    _create_broken_skill_placeholder(
                        skill_dir=skill_dir,
                        canonical_path=canonical,
                        agent=agent,
                        project_level=project_level,
                    )
                )
                continue

            if not skill_dir.is_dir():
                continue

            # Determine if this is a symlink
            skill_is_symlink = is_symlink(skill_dir)
            canonical_path: Path | None = None
            manifest_dir = skill_dir

            if skill_is_symlink:
                # Get the symlink target for symlinked skills
                canonical_path = get_symlink_target(skill_dir)
                # Read manifest from the canonical (target) location
                if canonical_path:
                    manifest_dir = canonical_path

            # Try to read the manifest
            manifest = read_manifest(manifest_dir)
            if manifest is None:
                continue

            # Extract skill name from directory name
            skill_name = skill_dir.name

            # Determine install mode from manifest or symlink status
            install_mode: InstallMode = "symlink" if skill_is_symlink else "copy"

            installed.append(
                InstalledSkill(
                    skill_id=manifest.skill_id,
                    skill_name=skill_name,
                    path=skill_dir,
                    manifest=manifest,
                    agent=agent,
                    project_level=project_level,
                    install_mode=install_mode,
                    canonical_path=canonical_path,
                    is_broken=False,
                )
            )

    except PermissionError:
        # Skip directories we can't read
        pass

    return installed


def _create_broken_skill_placeholder(
    skill_dir: Path,
    canonical_path: Path | None,
    agent: ExtendedAgentType,
    project_level: bool,
) -> InstalledSkill:
    """Create a placeholder InstalledSkill for a broken symlink.

    Args:
        skill_dir: Path to the broken symlink.
        canonical_path: The target path the symlink points to.
        agent: The agent type.
        project_level: Whether this is project-level.

    Returns:
        An InstalledSkill with is_broken=True and placeholder manifest.
    """
    # Create a minimal placeholder manifest for broken symlinks
    placeholder_manifest = SkillManifest(
        installed_at="unknown",
        skill_id=f"unknown/{skill_dir.name}",
        git_repo="unknown",
        skill_path="unknown",
        git_sha="unknown",
        skilz_version="unknown",
        install_mode="symlink",
        canonical_path=str(canonical_path) if canonical_path else None,
    )

    return InstalledSkill(
        skill_id=f"unknown/{skill_dir.name}",
        skill_name=skill_dir.name,
        path=skill_dir,
        manifest=placeholder_manifest,
        agent=agent,
        project_level=project_level,
        install_mode="symlink",
        canonical_path=canonical_path,
        is_broken=True,
    )


def scan_installed_skills(
    agent: ExtendedAgentType | None = None,
    project_level: bool = False,
    project_dir: Path | None = None,
    scan_all: bool = False,
) -> list[InstalledSkill]:
    """
    Scan for installed skills across all relevant directories.

    Args:
        agent: If specified, only scan for this agent type.
                If None, scan all known agents.
        project_level: If True, scan project-level directories.
                       If False, scan user-level directories.
        project_dir: Project directory for project-level scans.
        scan_all: If True, scan all registry agents. If False, scan top 5 agents.

    Returns:
        List of all installed skills found.
    """
    installed: list[InstalledSkill] = []

    # Determine which agents to scan
    if agent:
        # Specific agent requested
        agents_to_scan = [agent]
    else:
        # Get agents from registry
        registry = get_registry()

        if scan_all:
            # Scan all registry agents that support the requested level
            if project_level:
                all_agents = registry.list_agents()
            else:
                all_agents = registry.get_agents_with_home_support()
            agents_to_scan = cast(list[ExtendedAgentType], all_agents)
        else:
            # Scan top agents by default (covers 99% of users)
            if project_level:
                # For project level, use all top agents
                agents_to_scan = cast(list[ExtendedAgentType], TOP_AGENTS)
            else:
                # For user level, only agents with home support
                home_supported = registry.get_agents_with_home_support()
                agents_to_scan = cast(
                    list[ExtendedAgentType], [a for a in TOP_AGENTS if a in home_supported]
                )

    for scan_agent in agents_to_scan:
        skills_dir = get_skills_dir(
            agent=scan_agent,
            project_level=project_level,
            project_dir=project_dir,
        )

        found = scan_skills_directory(
            skills_dir=skills_dir,
            agent=scan_agent,  # type: ignore
            project_level=project_level,
        )
        installed.extend(found)

    # Sort by skill_id for consistent output
    installed.sort(key=lambda s: s.skill_id)

    return installed


def find_installed_skill(
    skill_id_or_name: str,
    agent: ExtendedAgentType | None = None,
    project_level: bool = False,
    project_dir: Path | None = None,
) -> InstalledSkill | None:
    """
    Find a specific installed skill by ID or name.

    Searches for exact match on skill_id first, then skill_name.
    If no exact match, tries partial match on skill_name.

    Args:
        skill_id_or_name: The skill ID (e.g., "spillwave/plantuml") or
                         name (e.g., "plantuml") to find.
        agent: If specified, only search this agent type.
        project_level: If True, search project-level installations.
        project_dir: Project directory for project-level searches.

    Returns:
        The InstalledSkill if found, None otherwise.
    """
    installed = scan_installed_skills(
        agent=agent,
        project_level=project_level,
        project_dir=project_dir,
    )

    # Try exact match on skill_id
    for skill in installed:
        if skill.skill_id == skill_id_or_name:
            return skill

    # Try exact match on skill_name
    for skill in installed:
        if skill.skill_name == skill_id_or_name:
            return skill

    # Try partial match on skill_name (for convenience)
    matches = [s for s in installed if skill_id_or_name.lower() in s.skill_name.lower()]

    if len(matches) == 1:
        return matches[0]

    # Ambiguous or not found
    return None
