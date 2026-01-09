"""API client for skillzwave.ai marketplace."""

import json
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from typing import Any

from skilz.errors import APIError

# API Configuration
API_BASE_URL = "https://skillzwave.ai/api"
API_TIMEOUT = 30  # seconds


@dataclass
class SkillCoordinates:
    """Skill coordinates returned from the API."""

    slug: str
    name: str
    description: str
    repo_full_name: str  # e.g., "Jamie-BitFlight/claude_skills"
    skill_path: str  # e.g., "holistic-linting/SKILL.md"
    branch: str  # e.g., "main"
    github_url: str
    raw_file_url: str
    score: float


def parse_skill_id(skill_id: str) -> tuple[str, str, str]:
    """
    Parse a skill ID into owner, repo, and skill_name.

    Supports three formats:
    - NEW:    owner/repo/skill_name  (2 slashes)
    - LEGACY: owner_repo/skill_name  (1 slash, underscore separates owner/repo)
    - SLUG:   owner__repo__skill     (double underscores, advanced users)

    Args:
        skill_id: The skill ID to parse

    Returns:
        Tuple of (owner, repo, skill_name)

    Raises:
        ValueError: If the skill_id format is invalid
    """
    # Check for SLUG format (double underscores)
    if "__" in skill_id:
        parts = skill_id.split("__")
        if len(parts) >= 3:
            owner = parts[0]
            repo = parts[1]
            skill_name = "__".join(parts[2:])  # Handle skill names with __
            if owner and repo and skill_name:
                return owner.lower(), repo.lower(), skill_name.lower()
        raise ValueError(f"Invalid slug format: '{skill_id}'. Expected format: owner__repo__skill")

    # Count slashes to determine format
    slash_count = skill_id.count("/")

    # NEW format: owner/repo/skill (2 slashes)
    if slash_count == 2:
        owner, repo, skill_name = skill_id.split("/")
        if owner and repo and skill_name:
            return owner, repo, skill_name
        raise ValueError(
            f"Invalid skill ID format: '{skill_id}'. Expected format: owner/repo/skill_name"
        )

    # LEGACY format: owner_repo/skill (1 slash with underscore)
    if slash_count == 1:
        owner_repo, skill_name = skill_id.rsplit("/", 1)
        if "_" not in owner_repo:
            raise ValueError(
                f"Invalid skill ID format: '{skill_id}'. "
                "Expected format: owner_repo/skill_name or owner/repo/skill_name"
            )
        # Split on FIRST underscore (GitHub owners can have hyphens, not underscores)
        idx = owner_repo.find("_")
        owner = owner_repo[:idx]
        repo = owner_repo[idx + 1 :]
        if owner and repo and skill_name:
            return owner, repo, skill_name
        raise ValueError(
            f"Invalid skill ID format: '{skill_id}'. "
            "Owner, repo, and skill_name must all be non-empty"
        )

    raise ValueError(
        f"Invalid skill ID format: '{skill_id}'. "
        "Expected: owner/repo/skill, owner_repo/skill, or owner__repo__skill"
    )


def is_marketplace_skill_id(skill_id: str) -> bool:
    """
    Check if a skill ID is in a recognized marketplace format.

    Recognized formats:
    - NEW:    owner/repo/skill_name  (2 slashes)
    - LEGACY: owner_repo/skill_name  (1 slash with underscore)
    - SLUG:   owner__repo__skill     (double underscores)

    Returns:
        True if the skill ID appears to be a marketplace skill ID
    """
    # SLUG format
    if "__" in skill_id:
        return skill_id.count("__") >= 2

    # NEW format: 2 slashes
    if skill_id.count("/") == 2:
        return True

    # LEGACY format: 1 slash with underscore before it
    if "/" in skill_id:
        owner_repo, _ = skill_id.rsplit("/", 1)
        return "_" in owner_repo

    return False


def get_skill_id_format(skill_id: str) -> str:
    """
    Determine the format type of a skill ID.

    Returns:
        One of: 'new', 'legacy', 'slug', 'unknown'
    """
    if "__" in skill_id and skill_id.count("__") >= 2:
        return "slug"
    if skill_id.count("/") == 2:
        return "new"
    if "/" in skill_id:
        owner_repo, _ = skill_id.rsplit("/", 1)
        if "_" in owner_repo:
            return "legacy"
    return "unknown"


def fetch_skill_by_name(
    owner: str,
    repo: str,
    skill_name: str,
    verbose: bool = False,
) -> SkillCoordinates:
    """
    Fetch skill coordinates by repository and skill name (path-agnostic).

    This uses the /api/skills/byname endpoint which searches by name,
    making it work for deeply nested skills regardless of path depth.

    Args:
        owner: Repository owner (e.g., "manutej")
        repo: Repository name (e.g., "luxor-claude-marketplace")
        skill_name: Skill name (e.g., "pytest-patterns")
        verbose: If True, print debug information

    Returns:
        SkillCoordinates with the skill's location data

    Raises:
        APIError: If the API request fails or skill not found
    """
    repo_full_name = f"{owner}/{repo}"
    url = (
        f"{API_BASE_URL}/skills/byname"
        f"?repoFullName={urllib.parse.quote(repo_full_name)}"
        f"&name={urllib.parse.quote(skill_name)}"
    )

    if verbose:
        print(f"  API lookup by name: {url}")

    result = _make_api_request(url, verbose)

    return SkillCoordinates(
        slug=result.get("slug", ""),
        name=result.get("name", skill_name),
        description=result.get("description", ""),
        repo_full_name=result.get("repoFullName", repo_full_name),
        skill_path=result.get("skillPath", ""),
        branch=result.get("branch", "main"),
        github_url=result.get("githubUrl", f"https://github.com/{repo_full_name}"),
        raw_file_url=result.get("rawFileUrl", ""),
        score=result.get("score", 0.0),
    )


def fetch_skill_coordinates(
    owner: str,
    repo: str,
    skill_name: str,
    verbose: bool = False,
) -> SkillCoordinates:
    """
    Fetch skill coordinates from the skillzwave.ai API.

    First tries the byname endpoint (works for any path depth),
    then falls back to coordinate lookup with path guessing.

    Args:
        owner: Repository owner (e.g., "Jamie-BitFlight")
        repo: Repository name (e.g., "claude_skills")
        skill_name: Skill name (e.g., "clang-format")
        verbose: If True, print debug information

    Returns:
        SkillCoordinates with the skill's location data

    Raises:
        APIError: If the API request fails or skill not found
    """
    repo_full_name = f"{owner}/{repo}"

    # First try the byname endpoint - works for any path depth
    try:
        return fetch_skill_by_name(owner, repo, skill_name, verbose)
    except APIError as e:
        if verbose:
            print(f"  Byname lookup failed: {e}, trying path patterns...")

    # Fallback: try coordinate lookup with common path patterns
    skill_paths_to_try = [
        f"{skill_name}/SKILL.md",
        f"skills/{skill_name}/SKILL.md",
        "SKILL.md",  # Root-level skill
    ]

    for skill_path in skill_paths_to_try:
        url = (
            f"{API_BASE_URL}/skills/coordinates"
            f"?owner={urllib.parse.quote(owner)}"
            f"&repo={urllib.parse.quote(repo)}"
            f"&path={urllib.parse.quote(skill_path)}"
        )

        if verbose:
            print(f"  Trying API: {url}")

        try:
            result = _make_api_request(url, verbose)

            return SkillCoordinates(
                slug=result.get("slug", ""),
                name=result.get("name", skill_name),
                description=result.get("description", ""),
                repo_full_name=result.get("repoFullName", repo_full_name),
                skill_path=result.get("skillPath", skill_path),
                branch=result.get("branch", "main"),
                github_url=result.get("githubUrl", f"https://github.com/{repo_full_name}"),
                raw_file_url=result.get("rawFileUrl", ""),
                score=result.get("score", 0.0),
            )

        except APIError as e:
            if "not found" in str(e).lower():
                continue  # Try next path
            raise  # Re-raise other errors

    # None of the paths worked
    raise APIError(
        f"Skill '{skill_name}' not found in repository '{repo_full_name}'. "
        f"Tried byname lookup and paths: {skill_paths_to_try}"
    )


def fetch_skill_by_slug(slug: str, verbose: bool = False) -> SkillCoordinates:
    """
    Fetch skill coordinates by slug (direct lookup).

    Args:
        slug: The skill slug (e.g., "Jamie-BitFlight__claude_skills__clang-format__SKILL")
        verbose: If True, print debug information

    Returns:
        SkillCoordinates with the skill's location data

    Raises:
        APIError: If the API request fails or skill not found
    """
    url = f"{API_BASE_URL}/skills/{urllib.parse.quote(slug)}/coordinates"

    if verbose:
        print(f"  API lookup by slug: {url}")

    result = _make_api_request(url, verbose)

    return SkillCoordinates(
        slug=result.get("slug", slug),
        name=result.get("name", ""),
        description=result.get("description", ""),
        repo_full_name=result.get("repoFullName", ""),
        skill_path=result.get("skillPath", ""),
        branch=result.get("branch", "main"),
        github_url=result.get("githubUrl", ""),
        raw_file_url=result.get("rawFileUrl", ""),
        score=result.get("score", 0.0),
    )


def _make_api_request(url: str, verbose: bool = False) -> dict[str, Any]:
    """
    Make an HTTP GET request to the API.

    Args:
        url: The full URL to request
        verbose: If True, print debug information

    Returns:
        Parsed JSON response as dictionary

    Raises:
        APIError: If the request fails
    """
    try:
        req = urllib.request.Request(
            url,
            headers={
                "Accept": "application/json",
                "User-Agent": "skilz-cli/0.1.0",
            },
        )

        with urllib.request.urlopen(req, timeout=API_TIMEOUT) as response:
            data: dict[str, Any] = json.loads(response.read().decode("utf-8"))

            # Check for error in response body
            if "error" in data:
                raise APIError(data["error"])

            return data

    except urllib.error.HTTPError as e:
        if e.code == 404:
            raise APIError("Skill not found (HTTP 404)")
        elif e.code == 400:
            body = e.read().decode("utf-8", errors="ignore")
            raise APIError(f"Bad request: {body}")
        else:
            raise APIError(f"API request failed: HTTP {e.code}")
    except urllib.error.URLError as e:
        raise APIError(f"Cannot connect to API: {e.reason}")
    except json.JSONDecodeError as e:
        raise APIError(f"Invalid API response: {e}")
    except TimeoutError:
        raise APIError(f"API request timed out after {API_TIMEOUT}s")
