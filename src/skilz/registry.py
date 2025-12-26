"""Registry loading and skill resolution."""

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

from skilz.errors import GitError, RegistryError, SkillNotFoundError


@dataclass
class SkillInfo:
    """Information about a skill from the registry."""

    skill_id: str
    git_repo: str
    skill_path: str
    git_sha: str

    @property
    def skill_name(self) -> str:
        """Extract the skill name from the skill_path or skill_id."""
        # Try to get from skill_path first (e.g., /main/skills/web-artifacts-builder)
        path_parts = self.skill_path.strip("/").split("/")

        if len(path_parts) >= 3:
            # e.g., /main/skills/web-artifacts-builder/SKILL.md -> web-artifacts-builder
            name = path_parts[-1]
            if name.endswith(".md"):
                name = path_parts[-2]
            if name and name != "SKILL":
                return name

        # Fall back to skill_id (e.g., anthropics/web-artifacts-builder -> web-artifacts-builder)
        # This handles cases like /main/SKILL.md where skill is at repo root
        return self.skill_id.split("/")[-1]


def get_registry_paths(project_dir: Path | None = None) -> list[Path]:
    """
    Get the list of registry paths to search, in priority order.

    Args:
        project_dir: The project directory to check for .skilz/registry.yaml.
                    If None, uses current working directory.

    Returns:
        List of registry paths to check, in order of priority.
    """
    paths = []

    # Project-level registry (highest priority)
    project = project_dir or Path.cwd()
    project_registry = project / ".skilz" / "registry.yaml"
    paths.append(project_registry)

    # User-level registry (fallback)
    user_registry = Path.home() / ".skilz" / "registry.yaml"
    paths.append(user_registry)

    return paths


def load_registry(path: Path) -> dict[str, Any]:
    """
    Load a registry file from the given path.

    Args:
        path: Path to the registry YAML file.

    Returns:
        Dictionary mapping skill IDs to their configuration.

    Raises:
        RegistryError: If the file cannot be read or parsed.
    """
    if not path.exists():
        raise RegistryError(str(path), "File not found")

    try:
        content = path.read_text()
        data = yaml.safe_load(content)

        if data is None:
            return {}

        if not isinstance(data, dict):
            raise RegistryError(str(path), "Registry must be a YAML dictionary")

        return data

    except yaml.YAMLError as e:
        raise RegistryError(str(path), f"Invalid YAML: {e}")
    except OSError as e:
        raise RegistryError(str(path), f"Cannot read file: {e}")


def lookup_skill(
    skill_id: str,
    project_dir: Path | None = None,
    verbose: bool = False,
    use_api: bool = True,
) -> SkillInfo:
    """
    Look up a skill by its ID in the registry or marketplace API.

    Searches project-level registry first, then user-level registry,
    then falls back to skillzwave.ai API if enabled.

    Args:
        skill_id: The skill ID to look up.
                  Legacy format: "anthropics/web-artifacts-builder"
                  Marketplace format: "Jamie-BitFlight_claude_skills/clang-format"
        project_dir: The project directory to check for .skilz/registry.yaml.
        verbose: If True, print debug information.
        use_api: If True, fall back to API when not found in local registries.

    Returns:
        SkillInfo with the skill's configuration.

    Raises:
        SkillNotFoundError: If the skill ID is not found anywhere.
        RegistryError: If a registry file exists but cannot be parsed.
        APIError: If API lookup fails (when use_api=True).
    """
    # Import here to avoid circular imports
    from skilz.api_client import (
        fetch_skill_coordinates,
        is_marketplace_skill_id,
        parse_skill_id,
    )
    from skilz.git_ops import fetch_github_sha

    registry_paths = get_registry_paths(project_dir)
    searched_paths: list[str] = []

    # Step 1: Try local registries first
    for registry_path in registry_paths:
        if not registry_path.exists():
            if verbose:
                print(f"  Registry not found: {registry_path}")
            continue

        searched_paths.append(str(registry_path))

        if verbose:
            print(f"  Searching registry: {registry_path}")

        try:
            registry = load_registry(registry_path)
        except RegistryError:
            raise

        if skill_id in registry:
            skill_data = registry[skill_id]

            required_fields = ["git_repo", "skill_path", "git_sha"]
            missing = [f for f in required_fields if f not in skill_data]
            if missing:
                raise RegistryError(
                    str(registry_path),
                    f"Skill '{skill_id}' missing required fields: {', '.join(missing)}",
                )

            if verbose:
                print(f"  Found skill '{skill_id}' in {registry_path}")

            return SkillInfo(
                skill_id=skill_id,
                git_repo=skill_data["git_repo"],
                skill_path=skill_data["skill_path"],
                git_sha=skill_data["git_sha"],
            )

    # Step 2: If marketplace format and API enabled, try API
    if use_api and is_marketplace_skill_id(skill_id):
        if verbose:
            print("  Not in local registries, trying marketplace API...")

        try:
            owner, repo, skill_name = parse_skill_id(skill_id)
            coords = fetch_skill_coordinates(owner, repo, skill_name, verbose=verbose)

            # Fetch SHA from GitHub (API doesn't provide it)
            # If this fails, fall back to "HEAD" - installer will resolve it
            git_sha: str
            sha_warning: str | None = None
            try:
                git_sha = fetch_github_sha(owner, repo, coords.branch, verbose=verbose)
            except GitError as sha_err:
                # GitHub API failed - use HEAD as fallback
                git_sha = "HEAD"
                sha_warning = (
                    f"Could not fetch SHA from GitHub ({sha_err.reason}), "
                    f"will use latest from {coords.branch}"
                )
                if verbose:
                    print(f"  Warning: {sha_warning}")

            # Build git_repo URL
            git_repo = f"https://github.com/{coords.repo_full_name}.git"

            # Build skill_path in skilz format: /{branch}/{path}
            skill_path = f"/{coords.branch}/{coords.skill_path}"

            if verbose:
                print(f"  Found via API: {coords.name}")
                print(f"  Repo: {git_repo}")
                print(f"  Path: {skill_path}")
                if git_sha != "HEAD":
                    print(f"  SHA: {git_sha[:8]}...")
                else:
                    print("  SHA: HEAD (will resolve during install)")

            # Print warning even in non-verbose mode
            if sha_warning and not verbose:
                print(f"Warning: {sha_warning}")

            return SkillInfo(
                skill_id=skill_id,
                git_repo=git_repo,
                skill_path=skill_path,
                git_sha=git_sha,
            )

        except Exception as e:
            if verbose:
                print(f"  API lookup failed: {e}")
            # Fall through to raise SkillNotFoundError

    # Not found anywhere
    raise SkillNotFoundError(skill_id, searched_paths)
