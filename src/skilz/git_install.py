"""Git URL installation for skilz.

This module handles installing skills directly from git repositories
without requiring registry entries.
"""

import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

from skilz.agents import AgentType
from skilz.errors import InstallError

# Type alias for install mode
InstallMode = Literal["copy", "symlink"]


@dataclass
class GitSkillInfo:
    """Information about a skill found in a git repository."""

    skill_name: str  # From frontmatter 'name:' field or directory name
    skill_path: Path  # Absolute path to skill directory in cloned repo
    relative_path: str  # Relative path from repo root


def parse_skill_name(skill_md_path: Path) -> str:
    """
    Parse skill name from SKILL.md frontmatter.

    Looks for 'name:' field in YAML frontmatter (between --- markers).
    Falls back to parent directory name if not found.

    Args:
        skill_md_path: Path to SKILL.md file.

    Returns:
        The skill name.
    """
    try:
        content = skill_md_path.read_text(encoding="utf-8")

        # Check for YAML frontmatter
        if content.startswith("---"):
            end_idx = content.find("---", 3)
            if end_idx > 0:
                frontmatter = content[3:end_idx]
                for line in frontmatter.split("\n"):
                    line = line.strip()
                    if line.startswith("name:"):
                        name_value = line.split(":", 1)[1].strip()
                        # Remove quotes if present
                        name_value = name_value.strip("'\"")
                        if name_value:
                            return name_value
    except OSError:
        pass

    # Fall back to directory name
    return skill_md_path.parent.name


def find_skills_in_repo(repo_path: Path) -> list[GitSkillInfo]:
    """
    Find all SKILL.md files in a cloned repository.

    Args:
        repo_path: Path to the cloned repository root.

    Returns:
        List of GitSkillInfo for each skill found.
    """
    skills: list[GitSkillInfo] = []

    # Find all SKILL.md files recursively
    for skill_md in repo_path.rglob("SKILL.md"):
        # Skip .git directory, but allow .claude/.opencode (these contain valid skills)
        relative_parts = skill_md.relative_to(repo_path).parts
        if ".git" in relative_parts:
            continue

        skill_dir = skill_md.parent
        skill_name = parse_skill_name(skill_md)
        relative_path = str(skill_dir.relative_to(repo_path))

        skills.append(
            GitSkillInfo(
                skill_name=skill_name,
                skill_path=skill_dir,
                relative_path=relative_path,
            )
        )

    # Sort by skill name for consistent ordering
    skills.sort(key=lambda s: s.skill_name.lower())

    return skills


def find_skills_from_marketplace(repo_path: Path) -> list[GitSkillInfo]:
    """
    Find skills from official Claude plugin marketplace.json.

    Looks for .claude-plugin/marketplace.json per official Claude Code docs.
    Falls back to checking root marketplace.json for compatibility.

    Reference: https://code.claude.com/docs/en/plugin-marketplaces

    Args:
        repo_path: Path to the cloned repository root.

    Returns:
        List of GitSkillInfo for each skill found in marketplace, or empty list.
    """
    # Official location per Claude Code docs, then fallback
    marketplace_paths = [
        repo_path / ".claude-plugin" / "marketplace.json",
        repo_path / "marketplace.json",
    ]

    for marketplace_path in marketplace_paths:
        if not marketplace_path.exists():
            continue

        try:
            data = json.loads(marketplace_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            continue

        skills: list[GitSkillInfo] = []

        # Official schema uses "plugins" array
        for plugin in data.get("plugins", []):
            source = plugin.get("source", "")

            # Handle string source (local path)
            if isinstance(source, str) and source.startswith("./"):
                skill_path = repo_path / source.lstrip("./")
            elif isinstance(source, str):
                skill_path = repo_path / source
            else:
                # Skip non-local sources (github refs, URLs)
                continue

            # Validate SKILL.md exists
            if (skill_path / "SKILL.md").exists():
                skills.append(
                    GitSkillInfo(
                        skill_name=plugin.get("name", skill_path.name),
                        skill_path=skill_path,
                        relative_path=str(skill_path.relative_to(repo_path)),
                    )
                )

        if skills:
            # Sort by skill name for consistent ordering
            skills.sort(key=lambda s: s.skill_name.lower())
            return skills

    return []


def prompt_skill_selection(
    skills: list[GitSkillInfo],
    install_all: bool = False,
    yes_all: bool = False,
) -> list[GitSkillInfo]:
    """
    Display numbered menu for skill selection.

    Args:
        skills: List of skills found in repository.
        install_all: If True, return all skills without prompting.
        yes_all: If True (global -y flag), return all skills without prompting.

    Returns:
        List of selected skills to install.
    """
    # If only one skill, return it directly
    if len(skills) == 1:
        return skills

    # If --all or -y flag, return all without prompting
    if install_all or yes_all:
        return skills

    # Display menu
    print(f"\nFound {len(skills)} skills in repository:\n")

    for i, skill in enumerate(skills, 1):
        path_info = f"  ({skill.relative_path})" if skill.relative_path != "." else ""
        print(f"  [{i}] {skill.skill_name}{path_info}")

    print("  [A] Install all")
    print("  [Q] Cancel")
    print()

    try:
        choice = input(f"Select skill(s) [1-{len(skills)}, A, Q]: ").strip()
    except (EOFError, KeyboardInterrupt):
        print()
        return []

    if not choice:
        return []

    choice_lower = choice.lower()

    # Handle 'all' selection
    if choice_lower in ("a", "all"):
        return skills

    # Handle cancel
    if choice_lower in ("q", "quit", "cancel"):
        return []

    # Handle comma-separated numbers
    selected: list[GitSkillInfo] = []
    try:
        # Split by comma and process each
        for part in choice.split(","):
            part = part.strip()
            if part:
                idx = int(part) - 1
                if 0 <= idx < len(skills):
                    if skills[idx] not in selected:
                        selected.append(skills[idx])
                else:
                    print(f"Invalid selection: {part}")
                    return []
    except ValueError:
        print(f"Invalid selection: {choice}")
        return []

    return selected


def get_head_sha(repo_path: Path) -> str:
    """
    Get the HEAD SHA of a cloned repository.

    Args:
        repo_path: Path to the cloned repository.

    Returns:
        The 40-character commit SHA.
    """
    import subprocess

    result = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=repo_path,
        capture_output=True,
        text=True,
    )

    if result.returncode == 0:
        return result.stdout.strip()

    return "unknown"


def install_from_git(
    git_url: str,
    agent: AgentType | None = None,
    project_level: bool = False,
    verbose: bool = False,
    mode: InstallMode | None = None,
    install_all: bool = False,
    yes_all: bool = False,
    skill_filter_name: str | None = None,
    force_config: bool = False,
    config_file: str | None = None,  # SKILZ-65: Custom config file for git installs
) -> int:
    """
    Install skill(s) from a git repository URL.

    Args:
        git_url: Git repository URL (HTTPS or SSH).
        agent: Target agent type.
        project_level: If True, install to project directory.
        verbose: If True, show detailed progress.
        mode: Installation mode ('copy' or 'symlink').
        install_all: If True, install all skills without prompting.
        yes_all: If True (global -y flag), install all without prompting.
        skill_filter_name: If provided, install only the skill with this name.
        force_config: If True, write to config files even for native agents.
        config_file: Optional custom config file to update (requires project_level=True).

    Returns:
        Exit code (0 for success, non-zero for error).
    """
    from skilz.installer import install_local_skill
    from skilz.link_ops import cleanup_temp_dir, clone_git_repo

    temp_dir: Path | None = None

    try:
        # Step 1: Clone repository
        if verbose:
            print(f"Cloning repository: {git_url}")

        try:
            temp_dir = clone_git_repo(git_url)
        except RuntimeError as e:
            print(f"Error: {e}", file=sys.stderr)
            return 1

        if verbose:
            print(f"Cloned to: {temp_dir}")

        # Step 2: Find all skills (try marketplace.json first, then recursive search)
        skills = find_skills_from_marketplace(temp_dir)
        if not skills:
            skills = find_skills_in_repo(temp_dir)

        if not skills:
            print(
                "Error: No skills found in repository. Skills must contain a SKILL.md file.",
                file=sys.stderr,
            )
            return 1

        if verbose:
            print(f"Found {len(skills)} skill(s)")

        # Step 3: Filter by skill name if --skill flag provided
        if skill_filter_name:
            matching = [s for s in skills if s.skill_name == skill_filter_name]
            if not matching:
                available = ", ".join(s.skill_name for s in skills)
                print(
                    f"Error: Skill '{skill_filter_name}' not found in repository.",
                    file=sys.stderr,
                )
                print(f"Available skills: {available}", file=sys.stderr)
                return 1
            selected = matching
        else:
            # Step 3b: Interactive selection
            selected = prompt_skill_selection(
                skills,
                install_all=install_all,
                yes_all=yes_all,
            )

        if not selected:
            if verbose:
                print("No skills selected.")
            return 0

        # Step 4: Get HEAD SHA for manifest
        head_sha = get_head_sha(temp_dir)

        # Step 5: Install each selected skill
        installed_count = 0
        failed_count = 0

        for skill in selected:
            try:
                if verbose or len(selected) > 1:
                    print(f"Installing: {skill.skill_name}")

                install_local_skill(
                    source_path=skill.skill_path,
                    agent=agent,
                    project_level=project_level,
                    verbose=verbose,
                    mode=mode,
                    # Override manifest fields for git source
                    git_url=git_url,
                    git_sha=head_sha,
                    # Use skill name from SKILL.md frontmatter
                    skill_name=skill.skill_name,
                    force_config=force_config,
                    config_file=config_file,  # SKILZ-65: Pass custom config file
                )

                installed_count += 1

            except InstallError as e:
                print(f"Failed to install {skill.skill_name}: {e}", file=sys.stderr)
                failed_count += 1

        # Step 6: Summary
        if len(selected) > 1:
            if failed_count == 0:
                print(f"\nInstalled {installed_count} skill(s) successfully.")
            else:
                print(
                    f"\nInstalled {installed_count} skill(s), {failed_count} failed.",
                    file=sys.stderr,
                )

        return 1 if failed_count > 0 else 0

    finally:
        # Step 7: Cleanup temp directory
        if temp_dir is not None:
            if verbose:
                print(f"Cleaning up: {temp_dir}")
            cleanup_temp_dir(temp_dir)
