"""Scanner for discovering installed skills."""

from dataclasses import dataclass
from pathlib import Path

from skilz.agents import AGENT_PATHS, AgentType, get_skills_dir
from skilz.manifest import SkillManifest, read_manifest


@dataclass
class InstalledSkill:
    """Represents an installed skill with its metadata."""

    skill_id: str
    skill_name: str
    path: Path
    manifest: SkillManifest
    agent: AgentType
    project_level: bool

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


def scan_skills_directory(
    skills_dir: Path,
    agent: AgentType,
    project_level: bool,
) -> list[InstalledSkill]:
    """
    Scan a skills directory for installed skills with manifests.

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
            if not skill_dir.is_dir():
                continue

            # Try to read the manifest
            manifest = read_manifest(skill_dir)
            if manifest is None:
                continue

            # Extract skill name from directory name
            skill_name = skill_dir.name

            installed.append(
                InstalledSkill(
                    skill_id=manifest.skill_id,
                    skill_name=skill_name,
                    path=skill_dir,
                    manifest=manifest,
                    agent=agent,
                    project_level=project_level,
                )
            )

    except PermissionError:
        # Skip directories we can't read
        pass

    return installed


def scan_installed_skills(
    agent: AgentType | None = None,
    project_level: bool = False,
    project_dir: Path | None = None,
) -> list[InstalledSkill]:
    """
    Scan for installed skills across all relevant directories.

    Args:
        agent: If specified, only scan for this agent type.
               If None, scan all known agents.
        project_level: If True, scan project-level directories.
                      If False, scan user-level directories.
        project_dir: Project directory for project-level scans.

    Returns:
        List of all installed skills found.
    """
    installed: list[InstalledSkill] = []

    # Determine which agents to scan
    agents_to_scan: list[AgentType] = [agent] if agent else list(AGENT_PATHS.keys())

    for scan_agent in agents_to_scan:
        skills_dir = get_skills_dir(
            agent=scan_agent,
            project_level=project_level,
            project_dir=project_dir,
        )

        found = scan_skills_directory(
            skills_dir=skills_dir,
            agent=scan_agent,
            project_level=project_level,
        )
        installed.extend(found)

    # Sort by skill_id for consistent output
    installed.sort(key=lambda s: s.skill_id)

    return installed


def find_installed_skill(
    skill_id_or_name: str,
    agent: AgentType | None = None,
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
