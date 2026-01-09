"""Tests for the visit command."""

from unittest.mock import MagicMock, patch

import pytest

from skilz.commands.visit_cmd import (
    MARKETPLACE_BASE_URL,
    check_url_exists,
    cmd_visit,
    open_in_browser,
    resolve_github_url,
    resolve_marketplace_url,
)


class TestResolveGithubUrl:
    """Tests for GitHub URL resolution."""

    def test_owner_repo_format(self):
        """owner/repo should resolve to GitHub URL."""
        url = resolve_github_url("anthropics/skills")
        assert url == "https://github.com/anthropics/skills"

    def test_owner_repo_path_format(self):
        """owner/repo/path should resolve to tree URL."""
        url = resolve_github_url("anthropics/skills/excel")
        assert url == "https://github.com/anthropics/skills/tree/main/excel"

    def test_nested_path(self):
        """Deep paths should work."""
        url = resolve_github_url("owner/repo/path/to/skill")
        assert url == "https://github.com/owner/repo/tree/main/path/to/skill"

    def test_https_passthrough(self):
        """HTTPS URLs should pass through."""
        input_url = "https://github.com/owner/repo"
        assert resolve_github_url(input_url) == input_url

    def test_http_passthrough(self):
        """HTTP URLs should pass through."""
        input_url = "http://github.com/owner/repo"
        assert resolve_github_url(input_url) == input_url

    def test_empty_raises_error(self):
        """Empty source should raise ValueError."""
        with pytest.raises(ValueError, match="cannot be empty"):
            resolve_github_url("")

    def test_whitespace_only_raises_error(self):
        """Whitespace-only source should raise ValueError."""
        with pytest.raises(ValueError, match="cannot be empty"):
            resolve_github_url("   ")

    def test_single_part_raises_error(self):
        """Single-part source should raise ValueError."""
        with pytest.raises(ValueError, match="Invalid source format"):
            resolve_github_url("just-one-part")

    def test_whitespace_handled(self):
        """Leading/trailing whitespace should be handled."""
        url = resolve_github_url("  owner/repo  ")
        assert url == "https://github.com/owner/repo"

    def test_empty_owner_raises_error(self):
        """Empty owner should raise ValueError."""
        with pytest.raises(ValueError, match="cannot be empty"):
            resolve_github_url("/repo")

    def test_empty_repo_raises_error(self):
        """Empty repo should raise ValueError."""
        with pytest.raises(ValueError, match="cannot be empty"):
            resolve_github_url("owner/")

    def test_full_github_url_with_path(self):
        """Full GitHub URL with path should pass through."""
        url = "https://github.com/owner/repo/tree/main/skill"
        assert resolve_github_url(url) == url


class TestResolveMarketplaceUrl:
    """Tests for marketplace URL resolution."""

    def test_owner_repo_skill_format(self):
        """owner/repo/skill should resolve to marketplace URL."""
        url = resolve_marketplace_url("Jamie-BitFlight/claude_skills/brainstorming-skill")
        expected = f"{MARKETPLACE_BASE_URL}/Jamie-BitFlight__claude_skills__brainstorming-skill/"
        assert url == expected

    def test_owner_repo_format(self):
        """owner/repo should resolve to marketplace URL."""
        url = resolve_marketplace_url("anthropics/skills")
        expected = f"{MARKETPLACE_BASE_URL}/anthropics__skills__skills/"
        assert url == expected

    def test_nested_skill_path(self):
        """owner/repo/path/to/skill should work."""
        url = resolve_marketplace_url("owner/repo/skills/xlsx")
        expected = f"{MARKETPLACE_BASE_URL}/owner__repo__xlsx/"
        assert url == expected

    def test_https_passthrough(self):
        """HTTPS URLs should pass through."""
        input_url = "https://skillzwave.ai/skill/some-skill/"
        assert resolve_marketplace_url(input_url) == input_url

    def test_empty_raises_error(self):
        """Empty source should raise ValueError."""
        with pytest.raises(ValueError, match="cannot be empty"):
            resolve_marketplace_url("")

    def test_single_skill_name(self):
        """Single skill name should be converted."""
        url = resolve_marketplace_url("my-skill")
        expected = f"{MARKETPLACE_BASE_URL}/spillwavesolutions__my-skill__my-skill/"
        assert url == expected


class TestCheckUrlExists:
    """Tests for URL existence checking."""

    @patch("skilz.commands.visit_cmd.urlopen")
    def test_returns_true_for_200(self, mock_urlopen):
        """Should return True for 200 response."""
        mock_response = MagicMock()
        mock_response.status = 200
        mock_urlopen.return_value = mock_response

        result = check_url_exists("https://example.com")
        assert result is True

    @patch("skilz.commands.visit_cmd.urlopen")
    def test_returns_false_for_non_200(self, mock_urlopen):
        """Should return False for non-200 response."""
        mock_response = MagicMock()
        mock_response.status = 404
        mock_urlopen.return_value = mock_response

        result = check_url_exists("https://example.com")
        assert result is False

    @patch("skilz.commands.visit_cmd.urlopen")
    def test_returns_false_on_url_error(self, mock_urlopen):
        """Should return False on URLError."""
        from urllib.error import URLError

        mock_urlopen.side_effect = URLError("Connection failed")

        result = check_url_exists("https://example.com")
        assert result is False

    @patch("skilz.commands.visit_cmd.urlopen")
    def test_returns_false_on_http_error(self, mock_urlopen):
        """Should return False on HTTPError."""
        from urllib.error import HTTPError

        mock_urlopen.side_effect = HTTPError("https://example.com", 404, "Not Found", {}, None)

        result = check_url_exists("https://example.com")
        assert result is False


class TestOpenInBrowser:
    """Tests for browser opening."""

    @patch("skilz.commands.visit_cmd.webbrowser.open")
    def test_opens_url(self, mock_open):
        """Should call webbrowser.open with URL."""
        mock_open.return_value = True
        result = open_in_browser("https://example.com")
        assert result is True
        mock_open.assert_called_once_with("https://example.com")

    @patch("skilz.commands.visit_cmd.webbrowser.open")
    def test_returns_false_on_browser_failure(self, mock_open):
        """Should return False when webbrowser.open returns False."""
        mock_open.return_value = False
        result = open_in_browser("https://example.com")
        assert result is False

    @patch("skilz.commands.visit_cmd.webbrowser.open")
    def test_handles_exception(self, mock_open):
        """Should return False on exception."""
        mock_open.side_effect = Exception("Browser failed")
        result = open_in_browser("https://example.com")
        assert result is False


class TestCmdVisit:
    """Tests for cmd_visit function."""

    @patch("skilz.commands.visit_cmd.open_in_browser")
    @patch("skilz.commands.visit_cmd.check_url_exists")
    def test_default_uses_marketplace_when_exists(self, mock_check, mock_browser, capsys):
        """Should use marketplace URL when it exists (default behavior)."""
        mock_check.return_value = True
        mock_browser.return_value = True

        args = MagicMock()
        args.source = "owner/repo/skill"
        args.git = False
        args.dry_run = False

        result = cmd_visit(args)

        assert result == 0
        # Should check marketplace first
        mock_check.assert_called_once()
        # Should open marketplace URL
        assert "skillzwave.ai" in mock_browser.call_args[0][0]

    @patch("skilz.commands.visit_cmd.open_in_browser")
    @patch("skilz.commands.visit_cmd.check_url_exists")
    def test_falls_back_to_github_when_marketplace_404(self, mock_check, mock_browser, capsys):
        """Should fall back to GitHub when marketplace returns 404."""
        mock_check.return_value = False
        mock_browser.return_value = True

        args = MagicMock()
        args.source = "owner/repo"
        args.git = False
        args.dry_run = False

        result = cmd_visit(args)

        assert result == 0
        # Should open GitHub URL
        assert "github.com" in mock_browser.call_args[0][0]

    @patch("skilz.commands.visit_cmd.open_in_browser")
    def test_git_flag_forces_github(self, mock_browser, capsys):
        """--git flag should force GitHub URL."""
        mock_browser.return_value = True

        args = MagicMock()
        args.source = "owner/repo"
        args.git = True
        args.dry_run = False

        result = cmd_visit(args)

        assert result == 0
        mock_browser.assert_called_once_with("https://github.com/owner/repo")

    @patch("skilz.commands.visit_cmd.open_in_browser")
    def test_git_flag_with_path(self, mock_browser, capsys):
        """--git flag should work with path."""
        mock_browser.return_value = True

        args = MagicMock()
        args.source = "owner/repo/skill"
        args.git = True
        args.dry_run = False

        result = cmd_visit(args)

        assert result == 0
        mock_browser.assert_called_once_with("https://github.com/owner/repo/tree/main/skill")

    def test_dry_run_outputs_url_without_opening(self, capsys):
        """--dry-run should output URL without opening browser."""
        args = MagicMock()
        args.source = "owner/repo/skill"
        args.git = True
        args.dry_run = True

        result = cmd_visit(args)

        assert result == 0
        captured = capsys.readouterr()
        assert "URL: https://github.com/owner/repo/tree/main/skill" in captured.out

    def test_dry_run_marketplace_url(self, capsys):
        """--dry-run should output marketplace URL by default."""
        args = MagicMock()
        args.source = "owner/repo/skill"
        args.git = False
        args.dry_run = True

        result = cmd_visit(args)

        assert result == 0
        captured = capsys.readouterr()
        assert "skillzwave.ai" in captured.out

    def test_invalid_source_returns_error(self, capsys):
        """Should return 1 and print error for invalid source."""
        args = MagicMock()
        args.source = "invalid"
        args.git = True  # Use git mode to hit the ValueError
        args.dry_run = False

        result = cmd_visit(args)

        assert result == 1
        captured = capsys.readouterr()
        assert "Error:" in captured.err
        assert "Invalid source format" in captured.err

    @patch("skilz.commands.visit_cmd.open_in_browser")
    def test_browser_failure_warning(self, mock_browser, capsys):
        """Should show warning when browser fails to open."""
        mock_browser.return_value = False

        args = MagicMock()
        args.source = "owner/repo"
        args.git = True
        args.dry_run = False

        result = cmd_visit(args)

        assert result == 0  # Still returns success
        captured = capsys.readouterr()
        assert "Warning: Could not open browser" in captured.err
        assert "https://github.com/owner/repo" in captured.out


class TestCLIIntegration:
    """Tests for CLI integration of visit command."""

    def test_visit_command_registered(self):
        """Visit command should be registered in CLI."""
        from skilz.cli import create_parser

        parser = create_parser()
        args = parser.parse_args(["visit", "owner/repo"])
        assert args.command == "visit"
        assert args.source == "owner/repo"

    def test_visit_git_flag(self):
        """Visit command should accept --git flag."""
        from skilz.cli import create_parser

        parser = create_parser()
        args = parser.parse_args(["visit", "owner/repo", "--git"])
        assert args.git is True

    def test_visit_git_short_flag(self):
        """Visit command should accept -g flag."""
        from skilz.cli import create_parser

        parser = create_parser()
        args = parser.parse_args(["visit", "-g", "owner/repo"])
        assert args.git is True

    def test_visit_dry_run_flag(self):
        """Visit command should accept --dry-run flag."""
        from skilz.cli import create_parser

        parser = create_parser()
        args = parser.parse_args(["visit", "owner/repo", "--dry-run"])
        assert args.dry_run is True

    def test_visit_combined_flags(self):
        """Visit command should accept multiple flags."""
        from skilz.cli import create_parser

        parser = create_parser()
        args = parser.parse_args(["visit", "-g", "--dry-run", "owner/repo"])
        assert args.git is True
        assert args.dry_run is True

    @patch("skilz.commands.visit_cmd.open_in_browser")
    def test_main_routes_to_visit_with_git(self, mock_browser, capsys):
        """main() should route visit command with --git to cmd_visit."""
        from skilz.cli import main

        mock_browser.return_value = True

        result = main(["visit", "--git", "owner/repo"])

        assert result == 0
        mock_browser.assert_called_once_with("https://github.com/owner/repo")

    def test_visit_dry_run_via_main(self, capsys):
        """main() should handle --dry-run."""
        from skilz.cli import main

        result = main(["visit", "--git", "--dry-run", "owner/repo"])

        assert result == 0
        captured = capsys.readouterr()
        assert "URL: https://github.com/owner/repo" in captured.out
