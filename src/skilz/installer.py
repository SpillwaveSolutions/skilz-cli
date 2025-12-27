"""Core installation logic for Skilz."""

import shutil
from pathlib import Path
from typing import cast

from skilz.agents import (
    AgentType,
    detect_agent,
    ensure_skills_dir,
    get_agent_default_mode,
    get_agent_display_name,
    supports_home_install,
)
from skilz.config_sync import SkillReference, sync_skill_to_configs
from skilz.errors import InstallError
from skilz.git_ops import (
    checkout_sha,
    clone_or_fetch,
    find_skill_by_name,
    get_branch_sha,
    get_skill_source_path,
    parse_skill_path,
    resolve_version_spec,
)
from skilz.link_ops import (
    InstallMode,
    create_symlink,
    determine_install_mode,
    ensure_canonical_copy,
    remove_skill,
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
        # Use symlinks=True to preserve symlinks instead of following them
        # Use ignore_dangling_symlinks=True to skip broken symlinks
        if verbose:
            print(f"  Copying {source_dir} -> {target_dir}")

        shutil.copytree(
            source_dir,
            target_dir,
            symlinks=True,
            ignore_dangling_symlinks=True,
        )

    except OSError as e:
        raise InstallError(str(source_dir), f"Failed to copy files: {e}")


def install_local_skill(
    source_path: Path,
    agent: AgentType | None = None,
    project_level: bool = False,
    verbose: bool = False,
    mode: InstallMode | None = None,
) -> None:
    """
    Install a skill from a local directory.

    Args:
        source_path: Path to the local skill directory.
        agent: Target agent ("claude" or "opencode"). Auto-detected if None.
        project_level: If True, install to project directory instead of user directory.
        verbose: If True, print detailed progress information.
        mode: Installation mode. Only "copy" is supported for local installs.
    """
    source_path = source_path.expanduser().resolve()

    if not source_path.exists():
        raise InstallError(str(source_path), "Source path does not exist")
    if not source_path.is_dir():
        raise InstallError(str(source_path), "Source path is not a directory")

    skill_name = source_path.name
    skill_id = f"local/{skill_name}"

    # Step 1: Determine target agent
    resolved_agent: AgentType
    if agent is None:
        resolved_agent = cast(AgentType, detect_agent())
        if verbose:
            print(f"Auto-detected agent: {get_agent_display_name(resolved_agent)}")
    else:
        resolved_agent = agent
        if verbose:
            print(f"Using specified agent: {get_agent_display_name(resolved_agent)}")

    # Step 1a: Auto-detect project-level for agents without home support
    if not project_level and not supports_home_install(resolved_agent):
        project_level = True
        if verbose:
            print(
                f"  Note: {get_agent_display_name(resolved_agent)} only supports "
                "project-level installation"
            )

    # Step 2: Determine target directory
    skills_dir = ensure_skills_dir(resolved_agent, project_level)
    target_dir = skills_dir / skill_name

    # Step 3: Copy files
    if verbose:
        print(f"Installing local skill '{skill_name}' to {target_dir}...")

    copy_skill_files(source_path, target_dir, verbose=verbose)

    # Step 4: Write manifest
    manifest = SkillManifest.create(
        skill_id=skill_id,
        git_repo="local",
        skill_path=str(source_path),
        git_sha="local",
        install_mode="copy",
    )
    write_manifest(target_dir, manifest)

    # Success message
    agent_name = get_agent_display_name(resolved_agent)
    location = "project" if project_level else "user"
    print(f"Installed: {skill_name} -> {agent_name} ({location}) [local]")

    # Step 5: Sync skill reference to agent config files (project-level only)
    if project_level:
        project_dir = Path.cwd()
        skill_ref = SkillReference(
            skill_id=skill_id,
            skill_name=skill_name,
            skill_path=target_dir,
        )

        if verbose:
            print("Syncing skill to config files...")

        sync_results = sync_skill_to_configs(
            skill=skill_ref,
            project_dir=project_dir,
            agent=resolved_agent if agent else None,
            verbose=verbose,
        )

        for result in sync_results:
            if result.error:
                print(f"  Warning: Could not update {result.config_file}: {result.error}")
            elif result.created:
                print(f"  Created: {result.config_file}")
            elif result.updated:
                if verbose:
                    print(f"  Updated: {result.config_file}")


def install_skill(
    skill_id: str,
    agent: AgentType | None = None,
    project_level: bool = False,
    verbose: bool = False,
    mode: InstallMode | None = None,
    version_spec: str | None = None,
) -> None:
    """
    Install a skill from the registry.

    Args:
        skill_id: The skill ID to install (e.g., "anthropics/web-artifacts-builder")
        agent: Target agent ("claude" or "opencode"). Auto-detected if None.
        project_level: If True, install to project directory instead of user directory.
        verbose: If True, print detailed progress information.
        mode: Installation mode ("copy" or "symlink"). If None, uses agent's default.
              - copy: Copies files directly to agent's skills directory.
              - symlink: Creates canonical copy in ~/.skilz/skills/, then symlinks.
        version_spec: Version specification to install:
              - None: Use marketplace version (default)
              - "latest": Latest commit from main branch
              - "branch:NAME": Latest commit from specified branch
              - 40-char hex: Specific commit SHA
              - Other: Treat as tag (tries "X" and "vX" formats)

    Raises:
        SkillNotFoundError: If the skill ID is not found in any registry.
        GitError: If Git operations fail.
        InstallError: If installation fails for other reasons.
    """
    # Step 1: Determine target agent
    resolved_agent: AgentType
    if agent is None:
        resolved_agent = cast(AgentType, detect_agent())
        if verbose:
            print(f"Auto-detected agent: {get_agent_display_name(resolved_agent)}")
    else:
        resolved_agent = agent
        if verbose:
            print(f"Using specified agent: {get_agent_display_name(resolved_agent)}")

    # Step 1a: Auto-detect project-level for agents without home support
    if not project_level and not supports_home_install(resolved_agent):
        project_level = True
        if verbose:
            print(
                f"  Note: {get_agent_display_name(resolved_agent)} only supports "
                "project-level installation"
            )

    # Step 1b: Determine installation mode
    agent_default: InstallMode = cast(InstallMode, get_agent_default_mode(resolved_agent))
    install_mode = determine_install_mode(mode, agent_default)

    if verbose:
        mode_source = "explicit" if mode else "agent default"
        print(f"Install mode: {install_mode} ({mode_source})")

    # Step 2: Look up skill in registry
    if verbose:
        print(f"Looking up skill: {skill_id}")

    skill_info: SkillInfo = lookup_skill(skill_id, verbose=verbose)

    if verbose:
        print(f"  Found: {skill_info.git_repo}")
        print(f"  Path: {skill_info.skill_path}")
        print(f"  SHA: {skill_info.git_sha[:8]}...")

    # Step 2b: Resolve version if specified
    resolved_sha = skill_info.git_sha
    if version_spec is not None:
        # Parse owner/repo from git URL
        # Handles: https://github.com/owner/repo.git or git@github.com:owner/repo.git
        git_url = skill_info.git_repo
        if "github.com" in git_url:
            # Extract owner/repo from URL
            if git_url.startswith("git@"):
                # git@github.com:owner/repo.git
                parts = git_url.split(":")[-1]
            else:
                # https://github.com/owner/repo.git
                parts = git_url.split("github.com/")[-1]
            parts = parts.rstrip(".git")
            owner_repo = parts.split("/")
            if len(owner_repo) >= 2:
                owner, repo = owner_repo[0], owner_repo[1]
                if verbose:
                    print(f"Resolving version '{version_spec}'...")
                resolved_sha = resolve_version_spec(
                    owner, repo, version_spec, skill_info.git_sha, verbose=verbose
                )
                if resolved_sha != skill_info.git_sha and verbose:
                    print(f"  Resolved to SHA: {resolved_sha[:8]}...")
        else:
            if verbose:
                print("  Warning: --version only supported for GitHub repos, using default")

    # Step 3: Determine target directory
    skills_dir = ensure_skills_dir(resolved_agent, project_level)
    target_dir = skills_dir / skill_info.skill_name

    # Step 4: Check if installation is needed
    should_install, reason = needs_install(target_dir, resolved_sha)

    if not should_install:
        print(f"Already installed: {skill_id} ({resolved_sha[:8]})")
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

    # Step 6b: Resolve "HEAD" to actual SHA if needed (fallback from API)
    if resolved_sha == "HEAD":
        if verbose:
            print(f"Resolving HEAD to actual SHA for branch '{branch}'...")
        resolved_sha = get_branch_sha(cache_path, branch, verbose=verbose)

    # Step 7: Checkout the specific SHA
    if verbose:
        print(f"Checking out {resolved_sha[:8]}...")

    checkout_sha(cache_path, resolved_sha, verbose=verbose)

    # Step 8: Get the source path within the repo
    source_dir = get_skill_source_path(cache_path, skill_info.skill_path)

    if not source_dir.exists():
        # Path not found - skill may have been reorganized in the repo
        # Try to find it by searching for SKILL.md files with matching name
        if verbose:
            print(f"  Path '{skill_info.skill_path}' not found, searching repository...")

        found_path = find_skill_by_name(cache_path, skill_info.skill_name, verbose=verbose)

        if found_path:
            source_dir = found_path
            if verbose:
                rel_path = source_dir.relative_to(cache_path)
                print(f"  Using found location: {rel_path}")
        else:
            raise InstallError(
                skill_id,
                f"Skill path not found in repository: {skill_info.skill_path}\n"
                f"Expected at: {source_dir}\n"
                f"Searched for skill named '{skill_info.skill_name}' but could not find it.\n"
                f"The skill may have been removed from the repository.",
            )

    # Step 9: Install files based on mode
    canonical_path: Path | None = None

    if install_mode == "symlink":
        # Symlink mode: create canonical copy, then symlink
        if verbose:
            print(f"Creating canonical copy in ~/.skilz/skills/{skill_info.skill_name}...")

        # Ensure canonical copy exists in ~/.skilz/skills/
        canonical_path = ensure_canonical_copy(
            source=source_dir,
            skill_name=skill_info.skill_name,
            global_install=True,  # Always use ~/.skilz/skills/
        )

        # Write manifest to canonical location first
        canonical_manifest = SkillManifest.create(
            skill_id=skill_info.skill_id,
            git_repo=skill_info.git_repo,
            skill_path=skill_info.skill_path,
            git_sha=resolved_sha,
            install_mode="symlink",
            canonical_path=str(canonical_path),
        )
        write_manifest(canonical_path, canonical_manifest)

        # Remove existing target (symlink or directory)
        if target_dir.exists() or target_dir.is_symlink():
            if verbose:
                print(f"Removing existing installation: {target_dir}")
            remove_skill(target_dir)

        # Create symlink from agent's skills dir to canonical
        if verbose:
            print(f"Creating symlink: {target_dir} -> {canonical_path}")

        create_symlink(source=canonical_path, target=target_dir)

    else:
        # Copy mode: copy directly to target
        if verbose:
            print(f"Copying to {target_dir}...")

        copy_skill_files(source_dir, target_dir, verbose=verbose)

        # Step 10: Write manifest
        manifest = SkillManifest.create(
            skill_id=skill_info.skill_id,
            git_repo=skill_info.git_repo,
            skill_path=skill_info.skill_path,
            git_sha=resolved_sha,
            install_mode="copy",
        )
        write_manifest(target_dir, manifest)

    # Success message
    action = "Updated" if reason == "sha_mismatch" else "Installed"
    agent_name = get_agent_display_name(resolved_agent)
    location = "project" if project_level else "user"
    mode_suffix = f" [{install_mode}]" if verbose else ""
    print(f"{action}: {skill_id} -> {agent_name} ({location}){mode_suffix}")

    # Step 11: Sync skill reference to agent config files (project-level only)
    if project_level:
        project_dir = Path.cwd()
        skill_ref = SkillReference(
            skill_id=skill_info.skill_id,
            skill_name=skill_info.skill_name,
            skill_path=target_dir,
        )

        if verbose:
            print("Syncing skill to config files...")

        # If agent was explicitly specified, only update that agent's config
        # Otherwise, update all existing config files in the project
        sync_results = sync_skill_to_configs(
            skill=skill_ref,
            project_dir=project_dir,
            agent=resolved_agent if agent else None,
            verbose=verbose,
        )

        # Report what was updated
        for result in sync_results:
            if result.error:
                print(f"  Warning: Could not update {result.config_file}: {result.error}")
            elif result.created:
                print(f"  Created: {result.config_file}")
            elif result.updated:
                if verbose:
                    print(f"  Updated: {result.config_file}")
