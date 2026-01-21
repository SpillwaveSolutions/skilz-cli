"""Symlink and copy operations for skill installation.

This module provides platform-aware operations for creating symbolic links
and copying skill directories. It handles edge cases like broken symlinks,
validation of skill sources, and graceful error handling.
"""

import shutil
import tempfile
from pathlib import Path
from typing import Literal

# Installation mode type
InstallMode = Literal["copy", "symlink"]


def create_symlink(source: Path, target: Path) -> None:
    """Create a symbolic link from target pointing to source.

    The symlink at `target` will point to `source`. This is the standard
    Unix symlink semantics where target is the new link being created.

    Args:
        source: The skill directory to link to (canonical location).
                Must exist and be a directory.
        target: Where to create the symlink (agent's skills dir).
                Parent directory will be created if needed.

    Raises:
        FileNotFoundError: If source does not exist.
        FileExistsError: If target already exists.
        OSError: If symlink creation fails (permissions, Windows without
                 developer mode, or filesystem doesn't support symlinks).
    """
    if not source.exists():
        raise FileNotFoundError(f"Source directory does not exist: {source}")

    if target.exists() or target.is_symlink():
        raise FileExistsError(f"Target already exists: {target}")

    # Ensure parent directory exists
    target.parent.mkdir(parents=True, exist_ok=True)

    # Create symlink (target_is_directory=True for directory symlinks)
    target.symlink_to(source.resolve(), target_is_directory=True)


def copy_skill(source: Path, target: Path) -> None:
    """Copy skill directory from source to target.

    Performs a complete directory copy. If target exists, it will be
    removed first to ensure a clean copy.

    Args:
        source: Source skill directory to copy from.
        target: Destination directory to copy to.

    Raises:
        FileNotFoundError: If source does not exist.
        NotADirectoryError: If source is not a directory.
        PermissionError: If lacking permissions to read source or write target.
    """
    if not source.exists():
        raise FileNotFoundError(f"Source directory does not exist: {source}")

    if not source.is_dir():
        raise NotADirectoryError(f"Source is not a directory: {source}")

    # Ensure parent directory exists
    target.parent.mkdir(parents=True, exist_ok=True)

    # Remove existing target if present
    if target.exists():
        shutil.rmtree(target)

    # Copy directory tree, preserving symlinks (don't follow them)
    # ignore_dangling_symlinks=True skips broken symlinks gracefully
    # SKILZ-089: Exclude .git directory to prevent nested repo issues
    shutil.copytree(
        source,
        target,
        symlinks=True,
        ignore_dangling_symlinks=True,
        ignore=shutil.ignore_patterns(".git"),
    )


def is_symlink(path: Path) -> bool:
    """Check if path is a symbolic link.

    Args:
        path: Path to check.

    Returns:
        True if path is a symlink (even if broken), False otherwise.
    """
    return path.is_symlink()


def get_symlink_target(path: Path) -> Path | None:
    """Get the resolved target of a symlink.

    Args:
        path: Path that may be a symlink.

    Returns:
        Resolved absolute path of symlink target, or None if not a symlink.
        For broken symlinks, returns the target path even if it doesn't exist.
    """
    if not path.is_symlink():
        return None

    # Use readlink to get the raw target, then resolve relative to parent
    raw_target = path.readlink()
    if raw_target.is_absolute():
        return raw_target
    else:
        # Resolve relative symlinks against the symlink's parent directory
        return (path.parent / raw_target).resolve()


def is_broken_symlink(path: Path) -> bool:
    """Check if path is a broken symbolic link.

    A broken symlink is one where the symlink exists but its target does not.

    Args:
        path: Path to check.

    Returns:
        True if path is a symlink pointing to a non-existent target,
        False otherwise (including if path doesn't exist at all).
    """
    # is_symlink() returns True even for broken symlinks
    # exists() returns False for broken symlinks
    return path.is_symlink() and not path.exists()


def validate_skill_source(path: Path) -> tuple[bool, str | None]:
    """Validate that a path contains a valid skill.

    Checks that the path exists, is a directory, and contains a SKILL.md file.

    Args:
        path: Path to validate as a skill source.

    Returns:
        Tuple of (is_valid, error_message).
        If valid, returns (True, None).
        If invalid, returns (False, "error description").
    """
    if not path.exists():
        return False, f"Path does not exist: {path}"

    if not path.is_dir():
        return False, f"Path is not a directory: {path}"

    skill_md = path / "SKILL.md"
    if not skill_md.exists():
        return False, f"Missing SKILL.md in: {path}"

    return True, None


def determine_install_mode(
    explicit_mode: InstallMode | None,
    agent_default: InstallMode,
) -> InstallMode:
    """Determine installation mode based on explicit flag and agent default.

    Priority order:
    1. Explicit mode flag (--copy or --symlink) - highest priority
    2. Agent's default_mode from registry

    Args:
        explicit_mode: Mode explicitly requested by user, or None.
        agent_default: Default mode from agent configuration.

    Returns:
        The installation mode to use ("copy" or "symlink").
    """
    if explicit_mode is not None:
        return explicit_mode
    return agent_default


def remove_skill(path: Path) -> bool:
    """Remove a skill, handling both symlinks and regular directories.

    For symlinks, only the symlink is removed, not the target.
    For regular directories, the entire directory tree is removed.

    Args:
        path: Path to the skill to remove.

    Returns:
        True if removal was successful, False if path didn't exist.

    Raises:
        PermissionError: If lacking permissions to remove.
    """
    if not path.exists() and not path.is_symlink():
        return False

    if path.is_symlink():
        # Just unlink the symlink, don't touch target
        path.unlink()
    else:
        # Remove directory tree
        shutil.rmtree(path)

    return True


def get_canonical_path(skill_name: str, global_install: bool = True) -> Path:
    """Get the canonical path for a skill in the universal directory.

    The canonical path is where the "master copy" of a skill lives,
    which symlinks point to.

    Args:
        skill_name: Name of the skill.
        global_install: If True, use ~/.skilz/skills/. If False, use .skilz/skills/.

    Returns:
        Path to the canonical skill location.
    """
    if global_install:
        return Path.home() / ".skilz" / "skills" / skill_name
    else:
        return Path.cwd() / ".skilz" / "skills" / skill_name


def ensure_canonical_copy(
    source: Path,
    skill_name: str,
    global_install: bool = True,
) -> Path:
    """Ensure a canonical copy exists in the universal directory.

    If the canonical copy doesn't exist, copies from source.
    If it already exists, returns the existing path.

    Args:
        source: Source skill directory to copy from if needed.
        skill_name: Name of the skill.
        global_install: If True, use ~/.skilz/skills/. If False, use .skilz/skills/.

    Returns:
        Path to the canonical skill location (guaranteed to exist after call).

    Raises:
        FileNotFoundError: If source doesn't exist.
    """
    canonical = get_canonical_path(skill_name, global_install)

    if not canonical.exists():
        copy_skill(source, canonical)

    return canonical


def clone_git_repo(url: str) -> Path:
    """Clone a git repository to a temporary directory.

    Args:
        url: Git repository URL (HTTPS or SSH).

    Returns:
        Path to the cloned repository (temporary directory).

    Raises:
        RuntimeError: If git clone fails.
    """
    import subprocess

    # Create temp directory that persists until explicitly cleaned up
    temp_dir = Path(tempfile.mkdtemp(prefix="skilz-git-"))

    try:
        result = subprocess.run(
            ["git", "clone", "--depth", "1", url, str(temp_dir)],
            capture_output=True,
            text=True,
            timeout=120,  # 2 minute timeout
        )

        if result.returncode != 0:
            # Clean up on failure
            shutil.rmtree(temp_dir, ignore_errors=True)
            raise RuntimeError(f"Git clone failed: {result.stderr}")

        return temp_dir

    except subprocess.TimeoutExpired:
        shutil.rmtree(temp_dir, ignore_errors=True)
        raise RuntimeError(f"Git clone timed out for: {url}")
    except FileNotFoundError:
        shutil.rmtree(temp_dir, ignore_errors=True)
        raise RuntimeError("Git is not installed or not in PATH")


def cleanup_temp_dir(path: Path) -> None:
    """Clean up a temporary directory created by clone_git_repo.

    Args:
        path: Path to temporary directory to remove.
    """
    if path.exists():
        shutil.rmtree(path, ignore_errors=True)


def get_skill_name_from_path(path: Path) -> str:
    """Extract skill name from a path.

    The skill name is the final component of the path (directory name).

    Args:
        path: Path to a skill directory.

    Returns:
        The skill name (directory name).
    """
    return path.name
