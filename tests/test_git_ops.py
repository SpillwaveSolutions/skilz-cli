"""Tests for the git_ops module."""

import subprocess
from unittest.mock import MagicMock, patch

import pytest

from skilz.errors import GitError
from skilz.git_ops import (
    checkout_sha,
    clone_or_fetch,
    clone_repo,
    fetch_repo,
    get_cache_path,
    get_skill_source_path,
    parse_skill_path,
    run_git_command,
)


class TestGetCachePath:
    """Tests for cache path generation."""

    def test_returns_path_under_skilz_cache(self):
        """Cache path should be under ~/.skilz/cache/."""
        path = get_cache_path("https://github.com/test/repo.git")
        assert ".skilz" in str(path)
        assert "cache" in str(path)

    def test_different_repos_get_different_paths(self):
        """Different repos should get different cache paths."""
        path1 = get_cache_path("https://github.com/test/repo1.git")
        path2 = get_cache_path("https://github.com/test/repo2.git")
        assert path1 != path2

    def test_same_repo_gets_same_path(self):
        """Same repo URL should always get the same cache path."""
        path1 = get_cache_path("https://github.com/test/repo.git")
        path2 = get_cache_path("https://github.com/test/repo.git")
        assert path1 == path2


class TestRunGitCommand:
    """Tests for run_git_command function."""

    @patch("subprocess.run")
    def test_success_returns_result(self, mock_run):
        """Successful command returns CompletedProcess."""
        mock_run.return_value = MagicMock(returncode=0, stdout="output", stderr="")

        result = run_git_command(["status"])

        mock_run.assert_called_once()
        assert result.returncode == 0

    @patch("subprocess.run")
    def test_failure_raises_git_error(self, mock_run):
        """Failed command raises GitError."""
        mock_run.return_value = MagicMock(
            returncode=1, stdout="", stderr="fatal: not a git repository"
        )

        with pytest.raises(GitError) as exc_info:
            run_git_command(["status"])

        assert "not a git repository" in str(exc_info.value)

    @patch("subprocess.run")
    def test_timeout_raises_git_error(self, mock_run):
        """Timeout raises GitError."""
        mock_run.side_effect = subprocess.TimeoutExpired(["git"], 300)

        with pytest.raises(GitError) as exc_info:
            run_git_command(["clone", "url"])

        assert "timed out" in str(exc_info.value).lower()

    @patch("subprocess.run")
    def test_git_not_found_raises_error(self, mock_run):
        """Missing git raises GitError."""
        mock_run.side_effect = FileNotFoundError()

        with pytest.raises(GitError) as exc_info:
            run_git_command(["status"])

        assert "not installed" in str(exc_info.value).lower()


class TestCloneRepo:
    """Tests for clone_repo function."""

    @patch("skilz.git_ops.run_git_command")
    @patch("skilz.git_ops.get_cache_path")
    def test_clone_new_repo(self, mock_cache_path, mock_git, temp_dir):
        """Clone a new repository."""
        cache_path = temp_dir / "cache" / "abc123"
        mock_cache_path.return_value = cache_path

        result = clone_repo("https://github.com/test/repo.git")

        mock_git.assert_called_once()
        assert "clone" in mock_git.call_args[0][0]
        assert result == cache_path

    @patch("skilz.git_ops.run_git_command")
    @patch("skilz.git_ops.get_cache_path")
    def test_skip_clone_if_cached(self, mock_cache_path, mock_git, temp_dir):
        """Skip clone if already cached."""
        cache_path = temp_dir / "cache" / "abc123"
        cache_path.mkdir(parents=True)
        mock_cache_path.return_value = cache_path

        result = clone_repo("https://github.com/test/repo.git")

        mock_git.assert_not_called()
        assert result == cache_path


class TestFetchRepo:
    """Tests for fetch_repo function."""

    @patch("skilz.git_ops.run_git_command")
    def test_fetch_existing_repo(self, mock_git, temp_dir):
        """Fetch in existing repo."""
        cache_path = temp_dir / "repo"
        cache_path.mkdir()

        fetch_repo(cache_path)

        mock_git.assert_called_once()
        assert "fetch" in mock_git.call_args[0][0]

    def test_fetch_nonexistent_raises_error(self, temp_dir):
        """Fetch in nonexistent directory raises error."""
        with pytest.raises(GitError) as exc_info:
            fetch_repo(temp_dir / "nonexistent")

        assert "does not exist" in str(exc_info.value)


class TestCheckoutSha:
    """Tests for checkout_sha function."""

    @patch("skilz.git_ops.run_git_command")
    def test_checkout_valid_sha(self, mock_git, temp_dir):
        """Checkout a valid SHA."""
        cache_path = temp_dir / "repo"
        cache_path.mkdir()

        checkout_sha(cache_path, "abc123def456")

        mock_git.assert_called_once()
        args = mock_git.call_args[0][0]
        assert "checkout" in args
        assert "abc123def456" in args

    @patch("skilz.git_ops.run_git_command")
    def test_checkout_invalid_sha_raises_error(self, mock_git, temp_dir):
        """Checkout invalid SHA raises descriptive error."""
        cache_path = temp_dir / "repo"
        cache_path.mkdir()
        mock_git.side_effect = GitError("checkout", "pathspec 'abc123' did not match any")

        with pytest.raises(GitError) as exc_info:
            checkout_sha(cache_path, "abc123")

        assert "not found" in str(exc_info.value).lower()


class TestCloneOrFetch:
    """Tests for clone_or_fetch function."""

    @patch("skilz.git_ops.fetch_repo")
    @patch("skilz.git_ops.clone_repo")
    @patch("skilz.git_ops.get_cache_path")
    def test_clone_if_not_cached(self, mock_cache_path, mock_clone, mock_fetch, temp_dir):
        """Clone if repo not in cache."""
        cache_path = temp_dir / "cache" / "abc123"
        mock_cache_path.return_value = cache_path
        mock_clone.return_value = cache_path

        result = clone_or_fetch("https://github.com/test/repo.git")

        mock_clone.assert_called_once()
        mock_fetch.assert_not_called()
        assert result == cache_path

    @patch("skilz.git_ops.fetch_repo")
    @patch("skilz.git_ops.clone_repo")
    @patch("skilz.git_ops.get_cache_path")
    def test_fetch_if_cached(self, mock_cache_path, mock_clone, mock_fetch, temp_dir):
        """Fetch if repo already in cache."""
        cache_path = temp_dir / "cache" / "abc123"
        cache_path.mkdir(parents=True)
        mock_cache_path.return_value = cache_path

        result = clone_or_fetch("https://github.com/test/repo.git")

        mock_clone.assert_not_called()
        mock_fetch.assert_called_once()
        assert result == cache_path


class TestGetSkillSourcePath:
    """Tests for get_skill_source_path function."""

    def test_full_path_with_skill_md(self, temp_dir):
        """Extract path from full skill path with SKILL.md."""
        result = get_skill_source_path(temp_dir, "/main/skills/my-skill/SKILL.md")
        assert result == temp_dir / "skills" / "my-skill"

    def test_path_without_skill_md(self, temp_dir):
        """Extract path without SKILL.md suffix."""
        result = get_skill_source_path(temp_dir, "/main/skills/my-skill")
        assert result == temp_dir / "skills" / "my-skill"

    def test_simple_path(self, temp_dir):
        """Simple path with just branch and skill."""
        result = get_skill_source_path(temp_dir, "/main/my-skill")
        assert result == temp_dir / "my-skill"

    def test_branch_only(self, temp_dir):
        """Path with only branch returns repo root."""
        result = get_skill_source_path(temp_dir, "/main")
        assert result == temp_dir


class TestParseSkillPath:
    """Tests for parse_skill_path function."""

    def test_full_path(self):
        """Parse full skill path."""
        branch, path = parse_skill_path("/main/skills/my-skill")
        assert branch == "main"
        assert path == "skills/my-skill"

    def test_branch_only(self):
        """Parse branch-only path."""
        branch, path = parse_skill_path("/v1.0.0")
        assert branch == "v1.0.0"
        assert path == ""

    def test_deep_path(self):
        """Parse deep path."""
        branch, path = parse_skill_path("/develop/src/skills/nested/deep/skill")
        assert branch == "develop"
        assert path == "src/skills/nested/deep/skill"
