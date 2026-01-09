"""Visit command for opening skill pages in browser."""

from __future__ import annotations

import argparse
import sys
import webbrowser
from urllib.error import HTTPError, URLError
from urllib.request import urlopen

# Marketplace base URL
MARKETPLACE_BASE_URL = "https://skillzwave.ai/agent-skill"


def resolve_github_url(source: str) -> str:
    """
    Resolve a source identifier to a GitHub URL.

    Args:
        source: Source identifier in one of these formats:
            - owner/repo: Basic repository path
            - owner/repo/path: Path within repository
            - https://github.com/...: Full URL (pass-through)
            - http://...: Full URL (pass-through)

    Returns:
        Full GitHub URL.

    Raises:
        ValueError: If source format is invalid.
    """
    source = source.strip()

    if not source:
        raise ValueError("Source cannot be empty")

    # Pass through full URLs
    if source.startswith("https://") or source.startswith("http://"):
        return source

    # Parse owner/repo format
    parts = source.split("/")

    if len(parts) < 2:
        raise ValueError(
            f"Invalid source format: '{source}'. Expected 'owner/repo' or 'owner/repo/path'"
        )

    owner = parts[0]
    repo = parts[1]

    if not owner or not repo:
        raise ValueError("Invalid source: owner and repo cannot be empty")

    # Basic owner/repo
    if len(parts) == 2:
        return f"https://github.com/{owner}/{repo}"

    # owner/repo/path - link to tree view
    path = "/".join(parts[2:])
    return f"https://github.com/{owner}/{repo}/tree/main/{path}"


def resolve_marketplace_url(source: str) -> str:
    """
    Resolve a source identifier to a marketplace URL.

    Args:
        source: Source identifier - typically a skill ID like:
            - owner/repo/skill-name
            - owner__repo__skill-name (already formatted)

    Returns:
        Full marketplace URL.

    Raises:
        ValueError: If source format is invalid.
    """
    source = source.strip()

    if not source:
        raise ValueError("Source cannot be empty")

    # Pass through full URLs
    if source.startswith("https://") or source.startswith("http://"):
        return source

    # Convert owner/repo/skill format to marketplace format
    # Marketplace uses: owner__repo__skill-name (no __SKILL suffix)
    parts = source.split("/")

    if len(parts) >= 3:
        # owner/repo/skill-name format
        owner = parts[0]
        repo = parts[1]
        skill_name = parts[-1]  # Last part is the skill name
        marketplace_id = f"{owner}__{repo}__{skill_name}"
    elif len(parts) == 2:
        # owner/repo format - assume skill name is repo name
        owner = parts[0]
        repo = parts[1]
        skill_name = repo  # Assume skill name = repo name
        marketplace_id = f"{owner}__{repo}__{skill_name}"
    elif len(parts) == 1:
        # Single name - assume it's a skill from spillwavesolutions organization
        skill_name = parts[0]
        # For single names, assume spillwavesolutions organization and skill name = repo name
        marketplace_id = f"spillwavesolutions__{skill_name}__{skill_name}"
    else:
        # Assume it's already a marketplace ID or skill name
        # Try to parse as owner__repo__skill format
        if "__" in source and source.count("__") >= 2:
            marketplace_id = source
        else:
            # Fallback: assume it's just a skill name, can't generate proper URL
            raise ValueError(
                f"Cannot generate marketplace URL for '{source}'. "
                "Expected format: owner/repo, owner/repo/skill-name, or skill-name"
            )

    return f"{MARKETPLACE_BASE_URL}/{marketplace_id}/"


def check_url_exists(url: str, timeout: float = 5.0) -> bool:
    """
    Check if a URL exists (returns 200).

    Args:
        url: URL to check.
        timeout: Request timeout in seconds.

    Returns:
        True if URL returns 200, False otherwise.
    """
    try:
        response = urlopen(url, timeout=timeout)
        return bool(response.status == 200)
    except (URLError, HTTPError):
        return False
    except Exception:
        return False


def open_in_browser(url: str) -> bool:
    """
    Open a URL in the default browser.

    Args:
        url: URL to open.

    Returns:
        True if browser was opened successfully, False otherwise.
    """
    try:
        return webbrowser.open(url)
    except Exception:
        return False


def cmd_visit(args: argparse.Namespace) -> int:
    """Execute the visit command.

    Args:
        args: Parsed command-line arguments.

    Returns:
        Exit code (0 for success, 1 for error).
    """
    source = args.source
    use_git = getattr(args, "git", False)
    dry_run = getattr(args, "dry_run", False)

    try:
        if use_git:
            # Force GitHub URL
            url = resolve_github_url(source)
        else:
            # Default: try marketplace first, fall back to GitHub
            marketplace_url = resolve_marketplace_url(source)

            if dry_run:
                # In dry-run mode, just show marketplace URL (don't check)
                url = marketplace_url
            else:
                # Check if marketplace URL exists
                print(f"Checking marketplace: {marketplace_url}")
                if check_url_exists(marketplace_url):
                    url = marketplace_url
                else:
                    print("Marketplace page not found, falling back to GitHub...")
                    url = resolve_github_url(source)

    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

    if dry_run:
        # Just output the URL, don't open browser
        print(f"URL: {url}")
        return 0

    print(f"Opening: {url}")

    if not open_in_browser(url):
        print("Warning: Could not open browser", file=sys.stderr)
        print(f"URL: {url}")

    return 0
