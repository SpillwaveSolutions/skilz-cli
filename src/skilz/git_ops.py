"""Git operations for cloning and checking out repositories."""

import hashlib
import subprocess
from pathlib import Path

from skilz.errors import GitError


def get_cache_dir() -> Path:
    """Get the cache directory for cloned repositories."""
    return Path.home() / ".skilz" / "cache"


def get_cache_path(git_repo: str) -> Path:
    """
    Get the cache path for a given repository.

    Uses a hash of the repo URL to avoid path collisions.

    Args:
        git_repo: The Git repository URL.

    Returns:
        Path to the cached repository directory.
    """
    repo_hash = hashlib.sha256(git_repo.encode()).hexdigest()[:12]
    return get_cache_dir() / repo_hash


def run_git_command(
    args: list[str],
    cwd: Path | None = None,
    check: bool = True,
    capture_output: bool = True,
) -> subprocess.CompletedProcess:
    """
    Run a git command and handle errors.

    Args:
        args: Git command arguments (without 'git' prefix).
        cwd: Working directory for the command.
        check: If True, raise GitError on non-zero exit code.
        capture_output: If True, capture stdout and stderr.

    Returns:
        CompletedProcess instance.

    Raises:
        GitError: If the command fails and check is True.
    """
    cmd = ["git"] + args
    try:
        result = subprocess.run(
            cmd,
            cwd=cwd,
            capture_output=capture_output,
            text=True,
            timeout=300,  # 5 minute timeout
        )

        if check and result.returncode != 0:
            error_msg = result.stderr.strip() or result.stdout.strip() or "Unknown error"
            raise GitError(" ".join(args[:2]), error_msg)

        return result

    except subprocess.TimeoutExpired:
        raise GitError(" ".join(args[:2]), "Command timed out after 5 minutes")
    except FileNotFoundError:
        raise GitError(" ".join(args[:2]), "Git is not installed or not in PATH")
    except OSError as e:
        raise GitError(" ".join(args[:2]), str(e))


def clone_repo(git_repo: str, verbose: bool = False) -> Path:
    """
    Clone a repository to the cache directory.

    Args:
        git_repo: The Git repository URL.
        verbose: If True, print progress information.

    Returns:
        Path to the cloned repository.

    Raises:
        GitError: If cloning fails.
    """
    cache_path = get_cache_path(git_repo)

    if cache_path.exists():
        if verbose:
            print(f"  Repository already cached: {cache_path}")
        return cache_path

    # Ensure cache directory exists
    cache_path.parent.mkdir(parents=True, exist_ok=True)

    if verbose:
        print(f"  Cloning {git_repo} to {cache_path}...")

    try:
        run_git_command(["clone", git_repo, str(cache_path)])
    except GitError as e:
        # Add more context to the error
        raise GitError(
            "clone",
            f"Failed to clone '{git_repo}': {e.reason}\n"
            "Check that the repository URL is correct and you have access.",
        )

    return cache_path


def fetch_repo(cache_path: Path, verbose: bool = False) -> None:
    """
    Fetch latest changes in a cached repository.

    Args:
        cache_path: Path to the cached repository.
        verbose: If True, print progress information.

    Raises:
        GitError: If fetching fails.
    """
    if not cache_path.exists():
        raise GitError("fetch", f"Cache directory does not exist: {cache_path}")

    if verbose:
        print(f"  Fetching latest changes in {cache_path}...")

    run_git_command(["fetch", "--all"], cwd=cache_path)


def checkout_sha(cache_path: Path, git_sha: str, verbose: bool = False) -> None:
    """
    Checkout a specific commit SHA in a cached repository.

    Args:
        cache_path: Path to the cached repository.
        git_sha: The commit SHA to checkout.
        verbose: If True, print progress information.

    Raises:
        GitError: If checkout fails (e.g., SHA not found).
    """
    if not cache_path.exists():
        raise GitError("checkout", f"Cache directory does not exist: {cache_path}")

    if verbose:
        print(f"  Checking out {git_sha[:8]}...")

    try:
        run_git_command(["checkout", git_sha], cwd=cache_path)
    except GitError as e:
        if "did not match any" in e.reason.lower() or "pathspec" in e.reason.lower():
            raise GitError(
                "checkout",
                f"Commit '{git_sha}' not found in repository.\n"
                "The registry may reference a commit that doesn't exist or hasn't been fetched.",
            )
        raise


def clone_or_fetch(git_repo: str, verbose: bool = False) -> Path:
    """
    Clone a repository or fetch updates if already cached.

    Args:
        git_repo: The Git repository URL.
        verbose: If True, print progress information.

    Returns:
        Path to the cached repository.

    Raises:
        GitError: If cloning or fetching fails.
    """
    cache_path = get_cache_path(git_repo)

    if cache_path.exists():
        # Repository already cached, fetch updates
        fetch_repo(cache_path, verbose=verbose)
    else:
        # Need to clone
        clone_repo(git_repo, verbose=verbose)

    return cache_path


def get_skill_source_path(cache_path: Path, skill_path: str) -> Path:
    """
    Get the source path for a skill within a cached repository.

    The skill_path format is: /<branch>/path/to/skill
    This function returns the path to the skill directory after checkout.

    Args:
        cache_path: Path to the cached repository.
        skill_path: The skill path from the registry (e.g., "/main/skills/my-skill").

    Returns:
        Path to the skill directory within the cached repo.
    """
    # Remove leading slash and split
    parts = skill_path.lstrip("/").split("/", 1)

    if len(parts) < 2:
        # Only branch specified, skill is at repo root
        return cache_path

    # parts[0] is branch (used for checkout), parts[1] is the actual path
    relative_path = parts[1]

    # Remove trailing SKILL.md if present (we want the directory)
    if relative_path.endswith("/SKILL.md"):
        relative_path = relative_path[:-9]  # Remove "/SKILL.md"
    elif relative_path.endswith("SKILL.md"):
        relative_path = relative_path[:-8]  # Remove "SKILL.md"
        if relative_path.endswith("/"):
            relative_path = relative_path[:-1]

    return cache_path / relative_path if relative_path else cache_path


def parse_skill_path(skill_path: str) -> tuple[str, str]:
    """
    Parse a skill path into branch and relative path components.

    Args:
        skill_path: The skill path from the registry (e.g., "/main/skills/my-skill").

    Returns:
        Tuple of (branch, relative_path).
    """
    parts = skill_path.lstrip("/").split("/", 1)
    branch = parts[0] if parts else "main"
    path = parts[1] if len(parts) > 1 else ""
    return branch, path


def fetch_github_sha(
    owner: str,
    repo: str,
    branch: str = "main",
    verbose: bool = False,
) -> str:
    """
    Fetch the latest commit SHA for a branch from GitHub API.

    Args:
        owner: Repository owner
        repo: Repository name
        branch: Branch name (default: "main")
        verbose: If True, print debug information

    Returns:
        The 40-character commit SHA

    Raises:
        GitError: If the request fails
    """
    import json
    import urllib.error
    import urllib.request

    url = f"https://api.github.com/repos/{owner}/{repo}/commits/{branch}"

    if verbose:
        print(f"  Fetching SHA from GitHub: {url}")

    try:
        req = urllib.request.Request(
            url,
            headers={
                "Accept": "application/vnd.github.v3+json",
                "User-Agent": "skilz-cli/0.1.0",
            },
        )

        with urllib.request.urlopen(req, timeout=30) as response:
            data = json.loads(response.read().decode("utf-8"))
            sha: str = data.get("sha", "")

            if not sha or len(sha) != 40:
                raise GitError("fetch_sha", f"Invalid SHA returned: {sha}")

            if verbose:
                print(f"  Got SHA: {sha[:8]}...")

            return sha

    except urllib.error.HTTPError as e:
        if e.code == 404:
            raise GitError("fetch_sha", f"Repository or branch not found: {owner}/{repo}@{branch}")
        raise GitError("fetch_sha", f"GitHub API error: HTTP {e.code}")
    except urllib.error.URLError as e:
        raise GitError("fetch_sha", f"Cannot connect to GitHub: {e.reason}")
    except json.JSONDecodeError:
        raise GitError("fetch_sha", "Invalid response from GitHub API")
