"""Tests for the visit command."""

from unittest.mock import MagicMock, patch

import pytest

from skilz.commands.visit_cmd import cmd_visit, open_in_browser, resolve_github_url


class TestResolveGithubUrl:
    """Tests for URL resolution."""

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
    def test_success(self, mock_browser, capsys):
        """Should open resolved URL in browser."""
        mock_browser.return_value = True

        args = MagicMock()
        args.source = "owner/repo"

        result = cmd_visit(args)

        assert result == 0
        mock_browser.assert_called_once_with("https://github.com/owner/repo")
        captured = capsys.readouterr()
        assert "Opening: https://github.com/owner/repo" in captured.out

    @patch("skilz.commands.visit_cmd.open_in_browser")
    def test_with_path(self, mock_browser, capsys):
        """Should handle owner/repo/path format."""
        mock_browser.return_value = True

        args = MagicMock()
        args.source = "owner/repo/skill"

        result = cmd_visit(args)

        assert result == 0
        mock_browser.assert_called_once_with("https://github.com/owner/repo/tree/main/skill")

    @patch("skilz.commands.visit_cmd.open_in_browser")
    def test_with_full_url(self, mock_browser, capsys):
        """Should handle full URL."""
        mock_browser.return_value = True

        args = MagicMock()
        args.source = "https://github.com/owner/repo"

        result = cmd_visit(args)

        assert result == 0
        mock_browser.assert_called_once_with("https://github.com/owner/repo")

    def test_invalid_source_returns_error(self, capsys):
        """Should return 1 and print error for invalid source."""
        args = MagicMock()
        args.source = "invalid"

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

    @patch("skilz.commands.visit_cmd.open_in_browser")
    def test_main_routes_to_visit(self, mock_browser, capsys):
        """main() should route visit command to cmd_visit."""
        from skilz.cli import main

        mock_browser.return_value = True

        result = main(["visit", "owner/repo"])

        assert result == 0
        mock_browser.assert_called_once()

    def test_visit_invalid_source_via_main(self, capsys):
        """main() should handle invalid source."""
        from skilz.cli import main

        result = main(["visit", "invalid"])

        assert result == 1
        captured = capsys.readouterr()
        assert "Error" in captured.err
