"""Search command for discovering skills on GitHub."""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from dataclasses import dataclass


@dataclass
class SearchResult:
    """A single search result."""

    full_name: str  # owner/repo
    description: str
    url: str
    stars: int = 0


def search_github_skills(
    query: str,
    limit: int = 10,
    verbose: bool = False,
) -> list[SearchResult]:
    """
    Search GitHub for skills matching the query.

    Uses gh CLI if available, falls back to basic repository search.

    Args:
        query: Search query string.
        limit: Maximum results to return.
        verbose: If True, print debug info.

    Returns:
        List of SearchResult objects.
    """
    # Check if gh CLI is available
    gh_path = shutil.which("gh")
    if not gh_path:
        print(
            "Warning: GitHub CLI (gh) not found. Install for search functionality.",
            file=sys.stderr,
        )
        return []

    # Check if authenticated
    auth_result = subprocess.run(
        ["gh", "auth", "status"],
        capture_output=True,
        text=True,
    )
    is_authenticated = auth_result.returncode == 0

    if verbose:
        auth_status = "authenticated" if is_authenticated else "not authenticated"
        print(f"GitHub CLI: {auth_status}")

    results: list[SearchResult] = []

    # Strategy: Search for repositories with skill-related topics or names
    try:
        search_query = f"{query} claude"

        # Build jq filter for parsing
        jq_filter = (
            ".items[:" + str(limit) + "] | .[] | "
            "{full_name, description, html_url, stargazers_count}"
        )

        result = subprocess.run(
            [
                "gh",
                "api",
                "-X",
                "GET",
                "search/repositories",
                "-f",
                f"q={search_query}",
                "-f",
                "sort=stars",
                "-f",
                "order=desc",
                "--jq",
                jq_filter,
            ],
            capture_output=True,
            text=True,
            timeout=30,
        )

        if result.returncode == 0 and result.stdout.strip():
            # Parse JSONL output (one object per line)
            for line in result.stdout.strip().split("\n"):
                if line:
                    try:
                        data = json.loads(line)
                        results.append(
                            SearchResult(
                                full_name=data.get("full_name", ""),
                                description=data.get("description", "") or "",
                                url=data.get("html_url", ""),
                                stars=data.get("stargazers_count", 0),
                            )
                        )
                    except json.JSONDecodeError:
                        continue

    except subprocess.TimeoutExpired:
        print("Warning: Search timed out", file=sys.stderr)
    except subprocess.SubprocessError as e:
        if verbose:
            print(f"Search error: {e}", file=sys.stderr)

    return results[:limit]


def format_results_table(results: list[SearchResult], query: str) -> str:
    """Format search results as a table."""
    if not results:
        return f"No skills found matching '{query}'"

    lines = [
        f"Found {len(results)} skill(s) matching '{query}':",
        "",
        f"{'NAME':<40} {'STARS':>6}  DESCRIPTION",
        "-" * 80,
    ]

    for r in results:
        name = r.full_name[:38] if len(r.full_name) > 38 else r.full_name
        desc = r.description[:30] if len(r.description) > 30 else r.description
        lines.append(f"{name:<40} {r.stars:>6}  {desc}")

    return "\n".join(lines)


def format_results_json(results: list[SearchResult], query: str) -> str:
    """Format search results as JSON."""
    data = {
        "query": query,
        "count": len(results),
        "results": [
            {
                "name": r.full_name,
                "description": r.description,
                "url": r.url,
                "stars": r.stars,
            }
            for r in results
        ],
    }
    return json.dumps(data, indent=2)


def cmd_search(args: argparse.Namespace) -> int:
    """Execute the search command.

    Args:
        args: Parsed command-line arguments.

    Returns:
        Exit code (0 for success).
    """
    query = args.query
    limit = getattr(args, "limit", 10)
    output_json = getattr(args, "json", False)
    verbose = getattr(args, "verbose", False)

    results = search_github_skills(query, limit=limit, verbose=verbose)

    if output_json:
        print(format_results_json(results, query))
    else:
        print(format_results_table(results, query))

    return 0
