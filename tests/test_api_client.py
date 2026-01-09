"""Tests for API client module."""

from unittest.mock import patch

import pytest

from skilz.api_client import (
    fetch_skill_coordinates,
    get_skill_id_format,
    is_marketplace_skill_id,
    parse_skill_id,
)
from skilz.errors import APIError


class TestParseSkillId:
    """Tests for parse_skill_id function."""

    def test_valid_marketplace_format(self):
        """Test parsing valid marketplace skill ID."""
        owner, repo, skill = parse_skill_id("Jamie-BitFlight_claude_skills/clang-format")
        assert owner == "Jamie-BitFlight"
        assert repo == "claude_skills"
        assert skill == "clang-format"

    def test_owner_with_hyphen(self):
        """Test parsing when owner contains hyphens."""
        owner, repo, skill = parse_skill_id("my-org_my-repo/my-skill")
        assert owner == "my-org"
        assert repo == "my-repo"
        assert skill == "my-skill"

    def test_repo_with_underscores(self):
        """Test parsing when repo name contains underscores."""
        # GitHub owners can't have underscores, so we split on FIRST underscore
        owner, repo, skill = parse_skill_id("my-owner_repo_with_underscores/skill")
        assert owner == "my-owner"
        assert repo == "repo_with_underscores"
        assert skill == "skill"

    def test_invalid_no_slash(self):
        """Test that missing slash raises ValueError."""
        with pytest.raises(ValueError, match="Expected:"):
            parse_skill_id("no-slash-here")

    def test_invalid_no_underscore(self):
        """Test that missing underscore raises ValueError."""
        with pytest.raises(ValueError, match="Expected format"):
            parse_skill_id("owner/skill")  # Legacy format, not marketplace

    def test_invalid_empty_parts(self):
        """Test that empty parts raise ValueError."""
        with pytest.raises(ValueError, match="must all be non-empty"):
            parse_skill_id("_repo/skill")


class TestIsMarketplaceSkillId:
    """Tests for is_marketplace_skill_id function."""

    def test_marketplace_format(self):
        """Test detection of marketplace format."""
        assert is_marketplace_skill_id("owner_repo/skill") is True
        assert is_marketplace_skill_id("Jamie-BitFlight_claude_skills/format") is True

    def test_legacy_format(self):
        """Test that legacy format returns False."""
        assert is_marketplace_skill_id("anthropics/web-artifacts") is False
        assert is_marketplace_skill_id("owner/skill") is False

    def test_no_slash(self):
        """Test that IDs without slash return False."""
        assert is_marketplace_skill_id("just-a-name") is False
        assert is_marketplace_skill_id("owner_repo") is False


class TestFetchSkillCoordinates:
    """Tests for fetch_skill_coordinates function."""

    @patch("skilz.api_client._make_api_request")
    def test_successful_fetch(self, mock_request):
        """Test successful API fetch."""
        mock_request.return_value = {
            "slug": "test__repo__skill__SKILL",
            "name": "skill",
            "description": "Test skill",
            "repoFullName": "test/repo",
            "skillPath": "skill/SKILL.md",
            "branch": "main",
            "githubUrl": "https://github.com/test/repo",
            "rawFileUrl": "https://raw.githubusercontent.com/test/repo/main/skill/SKILL.md",
            "score": 50.0,
        }

        result = fetch_skill_coordinates("test", "repo", "skill")

        assert result.name == "skill"
        assert result.repo_full_name == "test/repo"
        assert result.branch == "main"
        assert result.score == 50.0

    @patch("skilz.api_client._make_api_request")
    def test_skill_not_found(self, mock_request):
        """Test handling of skill not found."""
        mock_request.side_effect = APIError("Skill not found")

        with pytest.raises(APIError, match="not found"):
            fetch_skill_coordinates("test", "repo", "nonexistent")

    @patch("skilz.api_client._make_api_request")
    def test_tries_multiple_paths(self, mock_request):
        """Test that it tries multiple skill paths."""
        # First call fails (skill_name/SKILL.md), second succeeds (skills/skill_name/SKILL.md)
        mock_request.side_effect = [
            APIError("Skill not found"),
            {
                "slug": "test__repo__skills__skill__SKILL",
                "name": "skill",
                "repoFullName": "test/repo",
                "skillPath": "skills/skill/SKILL.md",
                "branch": "main",
            },
        ]

        result = fetch_skill_coordinates("test", "repo", "skill")

        assert result.skill_path == "skills/skill/SKILL.md"
        assert mock_request.call_count == 2


class TestParseSkillIdNewFormat:
    """Tests for NEW format: owner/repo/skill"""

    def test_new_format_basic(self):
        """Test NEW format: owner/repo/skill"""
        owner, repo, skill = parse_skill_id("davila7/claude-code-templates/slack-gif-creator")
        assert owner == "davila7"
        assert repo == "claude-code-templates"
        assert skill == "slack-gif-creator"

    def test_new_format_with_hyphens(self):
        """Test NEW format with hyphens in all parts"""
        owner, repo, skill = parse_skill_id("my-org/my-repo/my-skill")
        assert owner == "my-org"
        assert repo == "my-repo"
        assert skill == "my-skill"


class TestParseSkillIdSlugFormat:
    """Tests for SLUG format: owner__repo__skill"""

    def test_slug_format(self):
        """Test SLUG format: owner__repo__skill"""
        owner, repo, skill = parse_skill_id("davila7__claude-code-templates__slack-gif-creator")
        assert owner == "davila7"
        assert repo == "claude-code-templates"
        assert skill == "slack-gif-creator"

    def test_slug_format_lowercase(self):
        """Test SLUG format normalizes to lowercase"""
        owner, repo, skill = parse_skill_id("Davila7__Claude-Code-Templates__Slack-GIF-Creator")
        assert owner == "davila7"
        assert repo == "claude-code-templates"
        assert skill == "slack-gif-creator"


class TestIsMarketplaceSkillIdFormats:
    """Tests for is_marketplace_skill_id with all formats"""

    def test_new_format_is_marketplace(self):
        """NEW format is recognized as marketplace"""
        assert is_marketplace_skill_id("owner/repo/skill") is True

    def test_legacy_format_is_marketplace(self):
        """LEGACY format is recognized as marketplace"""
        assert is_marketplace_skill_id("owner_repo/skill") is True

    def test_slug_format_is_marketplace(self):
        """SLUG format is recognized as marketplace"""
        assert is_marketplace_skill_id("owner__repo__skill") is True

    def test_github_url_not_marketplace(self):
        """GitHub URL is not marketplace format"""
        assert is_marketplace_skill_id("https://github.com/owner/repo") is False

    def test_simple_path_not_marketplace(self):
        """Simple path is not marketplace format"""
        assert is_marketplace_skill_id("just-a-name") is False


class TestGetSkillIdFormat:
    """Tests for get_skill_id_format()"""

    def test_new_format_detected(self):
        """NEW format correctly detected"""
        assert get_skill_id_format("owner/repo/skill") == "new"

    def test_legacy_format_detected(self):
        """LEGACY format correctly detected"""
        assert get_skill_id_format("owner_repo/skill") == "legacy"

    def test_slug_format_detected(self):
        """SLUG format correctly detected"""
        assert get_skill_id_format("owner__repo__skill") == "slug"

    def test_unknown_format_detected(self):
        """Unknown format correctly detected"""
        assert get_skill_id_format("just-a-name") == "unknown"
        assert get_skill_id_format("owner/skill") == "unknown"  # Missing repo
