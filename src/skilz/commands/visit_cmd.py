"""Visit command for opening skill GitHub pages in browser."""

from __future__ import annotations

import argparse
import sys
import webbrowser


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

    try:
        url = resolve_github_url(source)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

    print(f"Opening: {url}")

    if not open_in_browser(url):
        print("Warning: Could not open browser", file=sys.stderr)
        print(f"URL: {url}")

    return 0
