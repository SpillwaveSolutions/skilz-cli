"""Tests for the search command."""

import json
from unittest.mock import MagicMock, patch

from skilz.commands.search_cmd import (
    SearchResult,
    cmd_search,
    format_results_json,
    format_results_table,
    search_github_skills,
)


class TestSearchResult:
    """Tests for SearchResult dataclass."""

    def test_create_result(self):
        """SearchResult should store all fields correctly."""
        result = SearchResult(
            full_name="owner/repo",
            description="A test skill",
            url="https://github.com/owner/repo",
            stars=100,
        )
        assert result.full_name == "owner/repo"
        assert result.description == "A test skill"
        assert result.url == "https://github.com/owner/repo"
        assert result.stars == 100

    def test_default_stars_is_zero(self):
        """Stars should default to 0."""
        result = SearchResult(
            full_name="owner/repo",
            description="test",
            url="https://example.com",
        )
        assert result.stars == 0


class TestFormatResultsTable:
    """Tests for format_results_table function."""

    def test_format_table_empty(self):
        """Empty results should show 'No skills found' message."""
        output = format_results_table([], "test")
        assert "No skills found matching 'test'" in output

    def test_format_table_with_results(self):
        """Should format results as table."""
        results = [
            SearchResult("owner/repo", "Test skill", "https://example.com", 50),
        ]
        output = format_results_table(results, "test")
        assert "owner/repo" in output
        assert "Test skill" in output
        assert "Found 1 skill(s)" in output
        assert "50" in output

    def test_format_table_truncates_long_names(self):
        """Should truncate long names."""
        results = [
            SearchResult(
                "very-long-organization-name/very-long-repository-name-here",
                "Description",
                "https://example.com",
                10,
            ),
        ]
        output = format_results_table(results, "test")
        # Name should be truncated but still present (partially)
        assert "very-long" in output

    def test_format_table_truncates_long_descriptions(self):
        """Should truncate long descriptions."""
        results = [
            SearchResult(
                "owner/repo",
                "This is a very long description that should be truncated to fit",
                "https://example.com",
                10,
            ),
        ]
        output = format_results_table(results, "test")
        # Description should be truncated
        assert "This is a very long" in output

    def test_format_table_multiple_results(self):
        """Should format multiple results."""
        results = [
            SearchResult("owner1/repo1", "First skill", "https://example.com", 100),
            SearchResult("owner2/repo2", "Second skill", "https://example.com", 50),
            SearchResult("owner3/repo3", "Third skill", "https://example.com", 25),
        ]
        output = format_results_table(results, "query")
        assert "Found 3 skill(s)" in output
        assert "owner1/repo1" in output
        assert "owner2/repo2" in output
        assert "owner3/repo3" in output


class TestFormatResultsJson:
    """Tests for format_results_json function."""

    def test_format_json_structure(self):
        """JSON output should have correct structure."""
        results = [
            SearchResult("owner/repo", "Test skill", "https://example.com", 50),
        ]
        output = format_results_json(results, "test")
        data = json.loads(output)
        assert data["query"] == "test"
        assert data["count"] == 1
        assert len(data["results"]) == 1
        assert data["results"][0]["name"] == "owner/repo"
        assert data["results"][0]["description"] == "Test skill"
        assert data["results"][0]["url"] == "https://example.com"
        assert data["results"][0]["stars"] == 50

    def test_format_json_empty_results(self):
        """Empty results should produce valid JSON."""
        output = format_results_json([], "test")
        data = json.loads(output)
        assert data["query"] == "test"
        assert data["count"] == 0
        assert data["results"] == []


class TestSearchGithubSkills:
    """Tests for search_github_skills function."""

    @patch("skilz.commands.search_cmd.shutil.which")
    def test_returns_empty_when_gh_not_found(self, mock_which, capsys):
        """Should return empty list when gh CLI not found."""
        mock_which.return_value = None
        results = search_github_skills("test")
        assert results == []
        captured = capsys.readouterr()
        assert "GitHub CLI (gh) not found" in captured.err

    @patch("skilz.commands.search_cmd.subprocess.run")
    @patch("skilz.commands.search_cmd.shutil.which")
    def test_parses_gh_output(self, mock_which, mock_run):
        """Should parse gh CLI output correctly."""
        mock_which.return_value = "/usr/bin/gh"

        # Mock auth status (authenticated)
        auth_result = MagicMock()
        auth_result.returncode = 0

        # Mock search result
        search_result = MagicMock()
        search_result.returncode = 0
        search_result.stdout = (
            '{"full_name":"owner/repo","description":"test skill",'
            '"html_url":"https://github.com/owner/repo","stargazers_count":42}'
        )

        mock_run.side_effect = [auth_result, search_result]

        results = search_github_skills("test", limit=5)

        assert len(results) == 1
        assert results[0].full_name == "owner/repo"
        assert results[0].description == "test skill"
        assert results[0].stars == 42

    @patch("skilz.commands.search_cmd.subprocess.run")
    @patch("skilz.commands.search_cmd.shutil.which")
    def test_handles_multiple_results(self, mock_which, mock_run):
        """Should handle multiple JSON lines."""
        mock_which.return_value = "/usr/bin/gh"

        auth_result = MagicMock()
        auth_result.returncode = 0

        search_result = MagicMock()
        search_result.returncode = 0
        search_result.stdout = (
            '{"full_name":"owner1/repo1","description":"skill1",'
            '"html_url":"https://1","stargazers_count":100}\n'
            '{"full_name":"owner2/repo2","description":"skill2",'
            '"html_url":"https://2","stargazers_count":50}'
        )

        mock_run.side_effect = [auth_result, search_result]

        results = search_github_skills("test", limit=10)

        assert len(results) == 2
        assert results[0].full_name == "owner1/repo1"
        assert results[1].full_name == "owner2/repo2"

    @patch("skilz.commands.search_cmd.subprocess.run")
    @patch("skilz.commands.search_cmd.shutil.which")
    def test_respects_limit(self, mock_which, mock_run):
        """Should respect the limit parameter."""
        mock_which.return_value = "/usr/bin/gh"

        auth_result = MagicMock()
        auth_result.returncode = 0

        # Return more results than the limit
        search_result = MagicMock()
        search_result.returncode = 0
        search_result.stdout = "\n".join(
            [
                f'{{"full_name":"owner/repo{i}","description":"skill{i}",'
                f'"html_url":"https://{i}","stargazers_count":{i}}}'
                for i in range(5)
            ]
        )

        mock_run.side_effect = [auth_result, search_result]

        results = search_github_skills("test", limit=3)

        assert len(results) == 3

    @patch("skilz.commands.search_cmd.subprocess.run")
    @patch("skilz.commands.search_cmd.shutil.which")
    def test_handles_empty_description(self, mock_which, mock_run):
        """Should handle null/empty descriptions."""
        mock_which.return_value = "/usr/bin/gh"

        auth_result = MagicMock()
        auth_result.returncode = 0

        search_result = MagicMock()
        search_result.returncode = 0
        search_result.stdout = (
            '{"full_name":"owner/repo","description":null,'
            '"html_url":"https://github.com/owner/repo","stargazers_count":10}'
        )

        mock_run.side_effect = [auth_result, search_result]

        results = search_github_skills("test")

        assert len(results) == 1
        assert results[0].description == ""

    @patch("skilz.commands.search_cmd.subprocess.run")
    @patch("skilz.commands.search_cmd.shutil.which")
    def test_handles_invalid_json_gracefully(self, mock_which, mock_run):
        """Should skip invalid JSON lines."""
        mock_which.return_value = "/usr/bin/gh"

        auth_result = MagicMock()
        auth_result.returncode = 0

        search_result = MagicMock()
        search_result.returncode = 0
        search_result.stdout = (
            "invalid json line\n"
            '{"full_name":"owner/repo","description":"valid",'
            '"html_url":"https://url","stargazers_count":10}'
        )

        mock_run.side_effect = [auth_result, search_result]

        results = search_github_skills("test")

        assert len(results) == 1
        assert results[0].full_name == "owner/repo"

    @patch("skilz.commands.search_cmd.subprocess.run")
    @patch("skilz.commands.search_cmd.shutil.which")
    def test_handles_timeout(self, mock_which, mock_run, capsys):
        """Should handle subprocess timeout gracefully."""
        mock_which.return_value = "/usr/bin/gh"

        auth_result = MagicMock()
        auth_result.returncode = 0

        import subprocess

        mock_run.side_effect = [auth_result, subprocess.TimeoutExpired(cmd="gh", timeout=30)]

        results = search_github_skills("test")

        assert results == []
        captured = capsys.readouterr()
        assert "timed out" in captured.err

    @patch("skilz.commands.search_cmd.subprocess.run")
    @patch("skilz.commands.search_cmd.shutil.which")
    def test_verbose_shows_auth_status(self, mock_which, mock_run, capsys):
        """Verbose mode should show auth status."""
        mock_which.return_value = "/usr/bin/gh"

        auth_result = MagicMock()
        auth_result.returncode = 0

        search_result = MagicMock()
        search_result.returncode = 0
        search_result.stdout = ""

        mock_run.side_effect = [auth_result, search_result]

        search_github_skills("test", verbose=True)

        captured = capsys.readouterr()
        assert "GitHub CLI: authenticated" in captured.out


class TestCmdSearch:
    """Tests for cmd_search function."""

    @patch("skilz.commands.search_cmd.search_github_skills")
    def test_cmd_search_basic(self, mock_search, capsys):
        """cmd_search should call search and print results."""
        mock_search.return_value = [
            SearchResult("owner/repo", "Test", "https://example.com", 10),
        ]

        args = MagicMock()
        args.query = "test"
        args.limit = 10
        args.json = False
        args.verbose = False

        result = cmd_search(args)

        assert result == 0
        mock_search.assert_called_once_with("test", limit=10, verbose=False)
        captured = capsys.readouterr()
        assert "owner/repo" in captured.out

    @patch("skilz.commands.search_cmd.search_github_skills")
    def test_cmd_search_json_output(self, mock_search, capsys):
        """cmd_search with --json should output JSON."""
        mock_search.return_value = [
            SearchResult("owner/repo", "Test", "https://example.com", 10),
        ]

        args = MagicMock()
        args.query = "test"
        args.limit = 10
        args.json = True
        args.verbose = False

        result = cmd_search(args)

        assert result == 0
        captured = capsys.readouterr()
        data = json.loads(captured.out)
        assert data["query"] == "test"


class TestCLIIntegration:
    """Tests for CLI integration of search command."""

    def test_search_command_registered(self):
        """Search command should be registered in CLI."""
        from skilz.cli import create_parser

        parser = create_parser()
        args = parser.parse_args(["search", "excel"])
        assert args.command == "search"
        assert args.query == "excel"

    def test_search_command_limit_option(self):
        """Search command should accept --limit option."""
        from skilz.cli import create_parser

        parser = create_parser()
        args = parser.parse_args(["search", "excel", "--limit", "5"])
        assert args.limit == 5

    def test_search_command_json_option(self):
        """Search command should accept --json option."""
        from skilz.cli import create_parser

        parser = create_parser()
        args = parser.parse_args(["search", "excel", "--json"])
        assert args.json is True

    def test_search_command_short_limit_option(self):
        """Search command should accept -l option."""
        from skilz.cli import create_parser

        parser = create_parser()
        args = parser.parse_args(["search", "excel", "-l", "3"])
        assert args.limit == 3

    @patch("skilz.commands.search_cmd.search_github_skills")
    def test_main_routes_to_search(self, mock_search):
        """main() should route search command to cmd_search."""
        from skilz.cli import main

        mock_search.return_value = []

        result = main(["search", "test"])

        assert result == 0
        mock_search.assert_called_once()
