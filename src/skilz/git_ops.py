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


def get_branch_sha(cache_path: Path, branch: str = "main", verbose: bool = False) -> str:
    """
    Get the current SHA for a branch in a cached repository.

    Tries the specified branch first, then falls back to origin/HEAD (default branch),
    then tries common default branch names (main, master).

    Args:
        cache_path: Path to the cached repository.
        branch: Branch name to get SHA for (default: main).
        verbose: If True, print progress information.

    Returns:
        The 40-character commit SHA.

    Raises:
        GitError: If no branch can be resolved.
    """
    if verbose:
        print(f"  Resolving HEAD for branch '{branch}'...")

    # Try branches in order of preference
    branches_to_try = [
        f"origin/{branch}",  # Remote specified branch
        branch,  # Local specified branch
        "origin/HEAD",  # Remote default branch
        "HEAD",  # Local HEAD
    ]

    # Add common defaults if not already the specified branch
    if branch != "main":
        branches_to_try.append("origin/main")
    if branch != "master":
        branches_to_try.append("origin/master")

    for ref in branches_to_try:
        result = run_git_command(
            ["rev-parse", ref],
            cwd=cache_path,
            check=False,
        )

        if result.returncode == 0:
            sha: str = result.stdout.strip()
            if len(sha) == 40:
                if verbose:
                    if ref != f"origin/{branch}" and ref != branch:
                        print(f"  Note: Branch '{branch}' not found, using '{ref}'")
                    print(f"  Resolved to: {sha[:8]}...")
                return sha

    raise GitError("rev-parse", f"Could not resolve SHA for branch '{branch}'")


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


def find_skill_by_name(cache_path: Path, skill_name: str, verbose: bool = False) -> Path | None:
    """
    Search for a skill by name when the expected path doesn't exist.

    This handles cases where skills have been reorganized in the repo
    but the registry/API has stale path data.

    Args:
        cache_path: Path to the cached repository.
        skill_name: The skill name to search for (e.g., "web-artifacts-builder").
        verbose: If True, print progress information.

    Returns:
        Path to the skill directory if found, None otherwise.
    """
    if verbose:
        print(f"  Searching for skill '{skill_name}' in repository...")

    # Find all SKILL.md files in the repo
    skill_files = list(cache_path.rglob("SKILL.md"))

    # Filter out .git directory matches
    skill_files = [p for p in skill_files if ".git" not in p.parts]

    if verbose:
        print(f"  Found {len(skill_files)} SKILL.md files")

    # Look for exact directory name match
    matches = []
    for skill_file in skill_files:
        skill_dir = skill_file.parent
        if skill_dir.name == skill_name:
            matches.append(skill_dir)

    if len(matches) == 1:
        if verbose:
            rel_path = matches[0].relative_to(cache_path)
            print(f"  Found skill at: {rel_path}")
        return matches[0]
    elif len(matches) > 1:
        if verbose:
            print(f"  Warning: Multiple matches found for '{skill_name}':")
            for match in matches:
                print(f"    - {match.relative_to(cache_path)}")
        # Return the first match (could be improved with more heuristics)
        return matches[0]

    # No exact match - try partial matching
    if verbose:
        print("  No exact match, checking SKILL.md files for name field...")

    for skill_file in skill_files:
        try:
            content = skill_file.read_text()
            # Check YAML frontmatter for name field
            if content.startswith("---"):
                end_idx = content.find("---", 3)
                if end_idx > 0:
                    frontmatter = content[3:end_idx]
                    for line in frontmatter.split("\n"):
                        if line.startswith("name:"):
                            name_value = line.split(":", 1)[1].strip().strip("'\"")
                            if name_value == skill_name:
                                if verbose:
                                    rel_path = skill_file.parent.relative_to(cache_path)
                                    print(f"  Found skill by name field at: {rel_path}")
                                return skill_file.parent
        except OSError:
            continue

    if verbose:
        print(f"  Could not find skill '{skill_name}' in repository")
    return None


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


def fetch_github_tag_sha(
    owner: str,
    repo: str,
    tag: str,
    verbose: bool = False,
) -> str:
    """
    Fetch the commit SHA for a specific tag from GitHub.

    Tries both 'tag' and 'v{tag}' formats.

    Args:
        owner: Repository owner.
        repo: Repository name.
        tag: Tag name (e.g., "1.0.1" or "v1.0.1").
        verbose: If True, print progress information.

    Returns:
        The commit SHA for the tag.

    Raises:
        GitError: If the tag is not found or API request fails.
    """
    import json
    import urllib.error
    import urllib.request

    # Try the tag as-is first, then with 'v' prefix
    tags_to_try = [tag]
    if not tag.startswith("v"):
        tags_to_try.append(f"v{tag}")

    for try_tag in tags_to_try:
        url = f"https://api.github.com/repos/{owner}/{repo}/git/refs/tags/{try_tag}"

        if verbose:
            print(f"  Fetching tag SHA from GitHub: {url}")

        try:
            req = urllib.request.Request(
                url,
                headers={
                    "Accept": "application/vnd.github.v3+json",
                    "User-Agent": "skilz-cli/1.0.2",
                },
            )

            with urllib.request.urlopen(req, timeout=30) as response:
                data = json.loads(response.read().decode("utf-8"))

                # The ref object contains the SHA
                obj = data.get("object", {})
                obj_type = str(obj.get("type", ""))
                sha: str = str(obj.get("sha", ""))

                # If it's a tag object (annotated tag), we need to dereference it
                if obj_type == "tag":
                    # Fetch the tag object to get the commit SHA
                    tag_url = obj.get("url", "")
                    if tag_url:
                        req2 = urllib.request.Request(
                            tag_url,
                            headers={
                                "Accept": "application/vnd.github.v3+json",
                                "User-Agent": "skilz-cli/1.0.2",
                            },
                        )
                        with urllib.request.urlopen(req2, timeout=30) as tag_response:
                            tag_data = json.loads(tag_response.read().decode("utf-8"))
                            sha = str(tag_data.get("object", {}).get("sha", ""))

                if sha and len(sha) == 40:
                    if verbose:
                        print(f"  Got SHA for tag '{try_tag}': {sha[:8]}...")
                    return sha

        except urllib.error.HTTPError as e:
            if e.code == 404:
                continue  # Try next tag format
            raise GitError("fetch_tag_sha", f"GitHub API error: HTTP {e.code}")
        except urllib.error.URLError as e:
            raise GitError("fetch_tag_sha", f"Cannot connect to GitHub: {e.reason}")
        except json.JSONDecodeError:
            raise GitError("fetch_tag_sha", "Invalid response from GitHub API")

    raise GitError("fetch_tag_sha", f"Tag not found: {tag} (tried: {', '.join(tags_to_try)})")


def resolve_version_spec(
    owner: str,
    repo: str,
    version_spec: str | None,
    default_sha: str,
    verbose: bool = False,
) -> str:
    """
    Resolve a version specification to a commit SHA.

    Version spec formats:
    - None: Use default_sha (from marketplace)
    - "latest": Get latest commit from main branch
    - "branch:NAME": Get latest commit from specified branch
    - 40-char hex string: Use as-is (commit SHA)
    - Other: Treat as tag (tries both "X" and "vX" formats)

    Args:
        owner: Repository owner.
        repo: Repository name.
        version_spec: The version specification string.
        default_sha: Default SHA to use if version_spec is None.
        verbose: If True, print progress information.

    Returns:
        The resolved commit SHA.

    Raises:
        GitError: If version resolution fails.
    """
    # No version spec - use default from marketplace
    if version_spec is None:
        if verbose:
            print(f"  Using marketplace version: {default_sha[:8]}...")
        return default_sha

    # "latest" - get latest from main
    if version_spec.lower() == "latest":
        if verbose:
            print("  Resolving 'latest' from main branch...")
        return fetch_github_sha(owner, repo, "main", verbose=verbose)

    # "branch:NAME" - get latest from specified branch
    if version_spec.lower().startswith("branch:"):
        branch = version_spec[7:]  # Remove "branch:" prefix
        if verbose:
            print(f"  Resolving latest from branch '{branch}'...")
        return fetch_github_sha(owner, repo, branch, verbose=verbose)

    # 40-character hex string - assume it's a commit SHA
    if len(version_spec) == 40 and all(c in "0123456789abcdefABCDEF" for c in version_spec):
        if verbose:
            print(f"  Using specified SHA: {version_spec[:8]}...")
        return version_spec.lower()

    # Short SHA (7-39 chars) - we'll use it but warn it might be ambiguous
    if 7 <= len(version_spec) <= 39 and all(c in "0123456789abcdefABCDEF" for c in version_spec):
        if verbose:
            print(f"  Using short SHA: {version_spec} (may need full SHA for checkout)")
        # We can't expand this without cloning, so just return it
        # Git will handle the lookup during checkout
        return version_spec.lower()

    # Otherwise, treat as a tag
    if verbose:
        print(f"  Resolving tag '{version_spec}'...")
    return fetch_github_tag_sha(owner, repo, version_spec, verbose=verbose)
