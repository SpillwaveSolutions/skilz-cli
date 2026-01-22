"""Install command implementation."""

import argparse
import sys
from pathlib import Path
from typing import Literal

from skilz.agents import AgentType
from skilz.errors import SkilzError


def is_git_url(skill_id: str | None) -> bool:
    """Detect if skill_id is a Git URL that should route to git installation.

    Detects:
    - HTTPS URLs: https://github.com/owner/repo
    - HTTP URLs: http://github.com/owner/repo
    - SSH URLs: git@github.com:owner/repo
    - .git suffix: any URL ending in .git

    Does NOT match:
    - Registry shorthand: owner/repo
    - Plain skill names: my-skill
    """
    if not skill_id:
        return False
    return (
        skill_id.startswith("https://")
        or skill_id.startswith("http://")
        or skill_id.startswith("git@")
        or skill_id.endswith(".git")
    )


def cmd_install(args: argparse.Namespace) -> int:
    """
    Handle the install command.

    Args:
        args: Parsed command-line arguments.

    Returns:
        Exit code (0 for success, non-zero for error).
    """
    # Import here to avoid circular imports and speed up --help
    from skilz.installer import install_local_skill, install_skill

    verbose = getattr(args, "verbose", False)
    agent: AgentType | None = getattr(args, "agent", None)
    project_level: bool = getattr(args, "project", False)
    skill_id: str | None = getattr(args, "skill_id", None)
    version_spec: str | None = getattr(args, "version_spec", None)
    force_config: bool = getattr(args, "force_config", False)
    config_file: str | None = getattr(args, "config", None)  # SKILZ-50

    # Validate --config flag (SKILZ-50)
    if config_file and not project_level:
        print("Error: --config requires --project flag", file=sys.stderr)
        return 1

    # Handle source options
    file_path: str | None = getattr(args, "file", None)
    git_url: str | None = getattr(args, "git", None)

    # AUTO-DETECT GIT URLs (SKILZ-48)
    # If skill_id looks like a URL, treat it as git installation
    if skill_id and is_git_url(skill_id) and not git_url:
        git_url = skill_id
        skill_id = None

    # NORMALIZE GITHUB SHORTHAND (owner/repo -> https://github.com/owner/repo)
    if git_url and not is_git_url(git_url):
        # If git_url doesn't look like a full URL, assume it's GitHub shorthand
        if "/" in git_url and not git_url.startswith("/"):
            git_url = f"https://github.com/{git_url}"

    # Validate source - exactly one of skill_id, -f, or -g must be provided
    sources = [s for s in [skill_id, file_path, git_url] if s is not None]
    if len(sources) == 0:
        print("Error: Must specify skill_id, --file, or --git", file=sys.stderr)
        return 1
    if len(sources) > 1:
        print("Error: Cannot use both skill_id and --file/--git options", file=sys.stderr)
        return 1

    # Determine installation mode from flags
    mode: Literal["copy", "symlink"] | None = None
    if getattr(args, "copy", False):
        mode = "copy"
    elif getattr(args, "symlink", False):
        mode = "symlink"

    # Handle -f and -g options
    if file_path is not None:
        try:
            install_local_skill(
                source_path=Path(file_path),
                agent=agent,
                project_level=project_level,
                verbose=verbose,
                mode=mode,
                force_config=force_config,
                config_file=config_file,  # SKILZ-50
            )
            return 0
        except SkilzError as e:
            print(f"Error: {e}", file=sys.stderr)
            return 1
        except Exception as e:
            print(f"Unexpected error: {e}", file=sys.stderr)
            return 1

    if git_url is not None:
        from skilz.git_install import install_from_git

        install_all = getattr(args, "install_all", False)
        yes_all = getattr(args, "yes_all", False)
        skill_filter_name: str | None = getattr(args, "skill", None)

        return install_from_git(
            git_url=git_url,
            agent=agent,
            project_level=project_level,
            verbose=verbose,
            mode=mode,
            install_all=install_all,
            yes_all=yes_all,
            skill_filter_name=skill_filter_name,
            force_config=force_config,
            config_file=config_file,  # SKILZ-65: Pass custom config file
        )

    try:
        install_skill(
            skill_id=skill_id,  # type: ignore[arg-type]
            agent=agent,
            project_level=project_level,
            verbose=verbose,
            mode=mode,
            version_spec=version_spec,
            force_config=force_config,
            config_file=config_file,  # SKILZ-50
        )
        return 0
    except SkilzError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        return 1
