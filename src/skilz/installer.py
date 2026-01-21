"""Core installation logic for Skilz."""

import shutil
import sys
from pathlib import Path
from typing import cast

from skilz.agent_registry import get_registry
from skilz.agents import (
    ExtendedAgentType,
    detect_agent,
    ensure_skills_dir,
    get_agent_default_mode,
    get_agent_display_name,
    supports_home_install,
)
from skilz.api_client import get_skill_id_format
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

        # SKILZ-089: Exclude .git directory to prevent nested repo issues
        shutil.copytree(
            source_dir,
            target_dir,
            symlinks=True,
            ignore_dangling_symlinks=True,
            ignore=shutil.ignore_patterns(".git"),
        )

    except OSError as e:
        raise InstallError(str(source_dir), f"Failed to copy files: {e}")


def install_local_skill(
    source_path: Path,
    agent: ExtendedAgentType | None = None,
    project_level: bool = False,
    verbose: bool = False,
    mode: InstallMode | None = None,
    git_url: str | None = None,
    git_sha: str | None = None,
    skill_name: str | None = None,
    force_config: bool = False,
    config_file: str | None = None,  # SKILZ-50: Custom config file target
) -> None:
    """
    Install a skill from a local directory.

    Args:
        source_path: Path to the local skill directory.
        agent: Target agent ("claude" or "opencode"). Auto-detected if None.
        project_level: If True, install to project directory instead of user directory.
        verbose: If True, print detailed progress information.
        mode: Installation mode. Only "copy" is supported for local installs.
        git_url: Optional git repo URL for manifest (overrides "local" default).
        git_sha: Optional git SHA for manifest (overrides "local" default).
        skill_name: Optional skill name (overrides source_path.name, used for git installs).
        force_config: If True, write to config files even for native agents.
        config_file: Optional config file to update (requires project_level=True).
    """
    source_path = source_path.expanduser().resolve()

    if not source_path.exists():
        raise InstallError(str(source_path), "Source path does not exist")
    if not source_path.is_dir():
        raise InstallError(str(source_path), "Source path is not a directory")

    # Use provided skill_name or fall back to directory name
    if skill_name is None:
        skill_name = source_path.name
    skill_id = f"local/{skill_name}"

    # Step 0: Validate skill name for native agents (Gemini, Claude, OpenCode)
    # This validation is only needed when agent is specified or can be detected
    resolved_agent_for_validation: ExtendedAgentType | None = None
    if agent is not None:
        resolved_agent_for_validation = agent
    else:
        # Try to detect agent early for validation
        try:
            resolved_agent_for_validation = cast(ExtendedAgentType, detect_agent())
        except Exception:
            pass  # Will be detected again later

    if resolved_agent_for_validation:
        from skilz.agent_registry import get_registry, validate_skill_name

        registry = get_registry()
        agent_config = registry.get(resolved_agent_for_validation)

        # Only validate for agents with native skill support
        if agent_config and agent_config.native_skill_support != "none":
            validation = validate_skill_name(skill_name)
            if not validation.is_valid:
                error_msg = f"Invalid skill name '{skill_name}' for {agent_config.display_name}.\n"
                error_msg += "\n".join(f"  - {err}" for err in validation.errors)
                if validation.suggested_name:
                    error_msg += f"\n\nSuggested name: {validation.suggested_name}"
                    error_msg += "\n\nUpdate your SKILL.md frontmatter:"
                    error_msg += f"\n---\nname: {validation.suggested_name}\ndescription: ...\n---"
                raise InstallError(str(source_path), error_msg)

            # Check if directory name matches skill name (skip for git installs with temp dirs)
            if git_url is None:  # Only validate permanent directories, not temp git clone dirs
                from skilz.agent_registry import check_skill_directory_name

                matches, suggested_path = check_skill_directory_name(source_path, skill_name)
                if not matches and suggested_path:
                    print(
                        f"Warning: Directory name '{source_path.name}' doesn't match "
                        f"skill name '{skill_name}'",
                        file=sys.stderr,
                    )
                    print(
                        f"  For better organization, consider renaming to: {suggested_path}",
                        file=sys.stderr,
                    )

    # Step 1: Determine target agent
    resolved_agent: ExtendedAgentType
    if agent is None:
        resolved_agent = cast(ExtendedAgentType, detect_agent())
        if verbose:
            print(f"Auto-detected agent: {get_agent_display_name(resolved_agent)}")
    else:
        resolved_agent = agent
        if verbose:
            print(f"Using specified agent: {get_agent_display_name(resolved_agent)}")

    # Step 1a: Auto-detect project-level for agents without home support
    if not project_level and not supports_home_install(resolved_agent):
        project_level = True
        # Always show message for Copilot, verbose for others
        if resolved_agent == "copilot":
            print(
                "  Info: GitHub Copilot only supports project-level installation (.github/skills/)"
            )
        elif verbose:
            agent_config = get_registry().get(resolved_agent)
            project_path = agent_config.project_dir if agent_config else ".skilz/skills"
            print(
                f"  Note: {get_agent_display_name(resolved_agent)} only supports "
                f"project-level installation ({project_path}/)"
            )

    # Step 2: Determine target directory
    skills_dir = ensure_skills_dir(resolved_agent, project_level)
    target_dir = skills_dir / skill_name

    # Step 3: Copy files
    if verbose:
        print(f"Installing local skill '{skill_name}' to {target_dir}...")

    copy_skill_files(source_path, target_dir, verbose=verbose)

    # Step 4: Write manifest
    # Use git info if provided (from -g/--git), otherwise mark as "local"
    is_git_source = git_url is not None
    manifest = SkillManifest.create(
        skill_id=f"git/{skill_name}" if is_git_source else skill_id,
        git_repo=git_url if git_url else "local",
        skill_path=str(source_path),
        git_sha=git_sha if git_sha else "local",
        install_mode="copy",
    )
    write_manifest(target_dir, manifest)

    # Success message
    agent_name = get_agent_display_name(resolved_agent)
    location = "project" if project_level else "user"
    source_label = "[git]" if is_git_source else "[local]"
    print(f"Installed: {skill_name} -> {agent_name} ({location}) {source_label}")

    # Step 5: Sync skill reference to agent config files (project-level only)
    if project_level:
        # Check if agent has native skill support (SKILZ-49)
        registry = get_registry()
        agent_config = registry.get_or_raise(resolved_agent)

        # Skip config sync for native agents unless --force-config or --config specified
        should_sync = (
            force_config or config_file is not None or agent_config.native_skill_support == "none"
        )

        if not should_sync:
            if verbose:
                print(
                    f"  Skipping config sync ({agent_config.display_name} has native skill support)"
                )
        else:
            project_dir = Path.cwd()
            ref_skill_id = f"git/{skill_name}" if is_git_source else skill_id
            skill_ref = SkillReference(
                skill_id=ref_skill_id,
                skill_name=skill_name,
                skill_path=target_dir,
            )

            if verbose:
                print("Syncing skill to config files...")

            # SKILZ-50: Use custom config file if provided
            target_files = (config_file,) if config_file else None

            sync_results = sync_skill_to_configs(
                skill=skill_ref,
                project_dir=project_dir,
                agent=resolved_agent if agent else None,
                verbose=verbose,
                target_files=target_files,
                force_extended=force_config,
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
    agent: ExtendedAgentType | None = None,
    project_level: bool = False,
    verbose: bool = False,
    mode: InstallMode | None = None,
    version_spec: str | None = None,
    force_config: bool = False,
    config_file: str | None = None,  # SKILZ-50: Custom config file target
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
        force_config: If True, write to config files even for native agents.
        config_file: Optional config file to update (requires project_level=True).

    Raises:
        SkillNotFoundError: If the skill ID is not found in any registry.
        GitError: If Git operations fail.
        InstallError: If installation fails for other reasons.
    """
    # Step 1: Determine target agent
    resolved_agent: ExtendedAgentType
    if agent is None:
        resolved_agent = cast(ExtendedAgentType, detect_agent())
        if verbose:
            print(f"Auto-detected agent: {get_agent_display_name(resolved_agent)}")
    else:
        resolved_agent = agent
        if verbose:
            print(f"Using specified agent: {get_agent_display_name(resolved_agent)}")

    # Step 1a: Auto-detect project-level for agents without home support
    if not project_level and not supports_home_install(resolved_agent):
        project_level = True
        # Always show message for Copilot, verbose for others
        if resolved_agent == "copilot":
            print(
                "  Info: GitHub Copilot only supports project-level installation (.github/skills/)"
            )
        elif verbose:
            agent_config = get_registry().get(resolved_agent)
            project_path = agent_config.project_dir if agent_config else ".skilz/skills"
            print(
                f"  Note: {get_agent_display_name(resolved_agent)} only supports "
                f"project-level installation ({project_path}/)"
            )

    # Step 1b: Determine installation mode
    agent_default: InstallMode = cast(InstallMode, get_agent_default_mode(resolved_agent))
    install_mode = determine_install_mode(mode, agent_default)

    if verbose:
        mode_source = "explicit" if mode else "agent default"
        print(f"Install mode: {install_mode} ({mode_source})")

    # Step 2: Look up skill in registry
    if verbose:
        format_type = get_skill_id_format(skill_id)
        print(f"Looking up skill: {skill_id}")
        print(f"  [INFO] Skill ID format: {format_type.upper()}")
        if format_type in ["new", "legacy", "slug"]:
            print("  [INFO] Attempting REST API lookup at skillzwave.ai...")

    skill_info: SkillInfo = lookup_skill(skill_id, verbose=verbose)

    if verbose:
        format_type = get_skill_id_format(skill_id)
        if format_type in ["new", "legacy", "slug"]:
            print(f"  [SUCCESS] REST API resolved skill: {skill_id}")
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
            # Always warn user about path change (not just verbose mode)
            print(
                f"Warning: Skill '{skill_info.skill_name}' found at different path than expected",
                file=sys.stderr,
            )
            if verbose:
                rel_path = source_dir.relative_to(cache_path)
                print(f"  Expected: {skill_info.skill_path}", file=sys.stderr)
                print(f"  Found at: {rel_path}", file=sys.stderr)
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
        # Check if agent has native skill support (SKILZ-49)
        registry = get_registry()
        agent_config = registry.get_or_raise(resolved_agent)

        # Skip config sync for native agents unless --force-config or --config specified
        should_sync = (
            force_config or config_file is not None or agent_config.native_skill_support == "none"
        )

        if not should_sync:
            if verbose:
                print(
                    f"  Skipping config sync ({agent_config.display_name} has native skill support)"
                )
        else:
            project_dir = Path.cwd()
            skill_ref = SkillReference(
                skill_id=skill_info.skill_id,
                skill_name=skill_info.skill_name,
                skill_path=target_dir,
            )

            if verbose:
                print("Syncing skill to config files...")

            # SKILZ-50: Use custom config file if provided
            target_files = (config_file,) if config_file else None

            # If agent was explicitly specified, only update that agent's config
            # Otherwise, update all existing config files in the project
            sync_results = sync_skill_to_configs(
                skill=skill_ref,
                project_dir=project_dir,
                agent=resolved_agent if agent else None,
                verbose=verbose,
                target_files=target_files,
                force_extended=force_config,
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
