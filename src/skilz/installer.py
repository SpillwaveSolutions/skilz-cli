"""Core installation logic for Skilz."""

import shutil
from pathlib import Path

from skilz.agents import AgentType, detect_agent, ensure_skills_dir, get_agent_display_name
from skilz.errors import InstallError
from skilz.git_ops import (
    checkout_sha,
    clone_or_fetch,
    get_skill_source_path,
    parse_skill_path,
)
from skilz.manifest import SkillManifest, needs_install, write_manifest
from skilz.registry import SkillInfo, lookup_skill


def copy_skill_files(source_dir: Path, target_dir: Path, verbose: bool = False) -> None:
    """
    Copy skill files from source to target directory.

    Args:
        source_dir: Source directory (in cache).
        target_dir: Target directory (in agent skills dir).
        verbose: If True, print progress information.

    Raises:
        InstallError: If copying fails.
    """
    if not source_dir.exists():
        raise InstallError(
            str(source_dir),
            f"Source directory does not exist: {source_dir}",
        )

    if not source_dir.is_dir():
        raise InstallError(
            str(source_dir),
            f"Source is not a directory: {source_dir}",
        )

    try:
        # Remove existing target if it exists
        if target_dir.exists():
            if verbose:
                print(f"  Removing existing installation: {target_dir}")
            shutil.rmtree(target_dir)

        # Ensure parent directory exists
        target_dir.parent.mkdir(parents=True, exist_ok=True)

        # Copy the skill directory
        if verbose:
            print(f"  Copying {source_dir} -> {target_dir}")

        shutil.copytree(source_dir, target_dir)

    except OSError as e:
        raise InstallError(str(source_dir), f"Failed to copy files: {e}")


def install_skill(
    skill_id: str,
    agent: AgentType | None = None,
    project_level: bool = False,
    verbose: bool = False,
) -> None:
    """
    Install a skill from the registry.

    Args:
        skill_id: The skill ID to install (e.g., "anthropics/web-artifacts-builder")
        agent: Target agent ("claude" or "opencode"). Auto-detected if None.
        project_level: If True, install to project directory instead of user directory.
        verbose: If True, print detailed progress information.

    Raises:
        SkillNotFoundError: If the skill ID is not found in any registry.
        GitError: If Git operations fail.
        InstallError: If installation fails for other reasons.
    """
    # Step 1: Determine target agent
    if agent is None:
        agent = detect_agent()
        if verbose:
            print(f"Auto-detected agent: {get_agent_display_name(agent)}")
    else:
        if verbose:
            print(f"Using specified agent: {get_agent_display_name(agent)}")

    # Step 2: Look up skill in registry
    if verbose:
        print(f"Looking up skill: {skill_id}")

    skill_info: SkillInfo = lookup_skill(skill_id, verbose=verbose)

    if verbose:
        print(f"  Found: {skill_info.git_repo}")
        print(f"  Path: {skill_info.skill_path}")
        print(f"  SHA: {skill_info.git_sha[:8]}...")

    # Step 3: Determine target directory
    skills_dir = ensure_skills_dir(agent, project_level)
    target_dir = skills_dir / skill_info.skill_name

    # Step 4: Check if installation is needed
    should_install, reason = needs_install(target_dir, skill_info.git_sha)

    if not should_install:
        print(f"Already installed: {skill_id} ({skill_info.git_sha[:8]})")
        return

    if verbose:
        if reason == "sha_mismatch":
            print("  Updating: SHA changed")
        elif reason == "no_manifest":
            print("  Reinstalling: no manifest found")
        else:
            print(f"  Installing: {reason}")

    # Step 5: Clone or fetch repository
    if verbose:
        print("Fetching repository...")

    cache_path = clone_or_fetch(skill_info.git_repo, verbose=verbose)

    # Step 6: Parse skill path to get branch
    branch, _ = parse_skill_path(skill_info.skill_path)

    # Step 7: Checkout the specific SHA
    if verbose:
        print(f"Checking out {skill_info.git_sha[:8]}...")

    checkout_sha(cache_path, skill_info.git_sha, verbose=verbose)

    # Step 8: Get the source path within the repo
    source_dir = get_skill_source_path(cache_path, skill_info.skill_path)

    if not source_dir.exists():
        raise InstallError(
            skill_id,
            f"Skill path not found in repository: {skill_info.skill_path}\n"
            f"Expected at: {source_dir}",
        )

    # Step 9: Copy files to target
    if verbose:
        print(f"Installing to {target_dir}...")

    copy_skill_files(source_dir, target_dir, verbose=verbose)

    # Step 10: Write manifest
    manifest = SkillManifest.create(
        skill_id=skill_info.skill_id,
        git_repo=skill_info.git_repo,
        skill_path=skill_info.skill_path,
        git_sha=skill_info.git_sha,
    )
    write_manifest(target_dir, manifest)

    # Success message
    action = "Updated" if reason == "sha_mismatch" else "Installed"
    agent_name = get_agent_display_name(agent)
    location = "project" if project_level else "user"
    print(f"{action}: {skill_id} -> {agent_name} ({location})")
