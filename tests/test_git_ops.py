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


class TestGetBranchSha:
    """Tests for get_branch_sha function."""

    @patch("skilz.git_ops.run_git_command")
    def test_resolves_origin_branch(self, mock_git, temp_dir):
        """Resolves origin/branch first."""
        from skilz.git_ops import get_branch_sha

        cache_path = temp_dir / "repo"
        cache_path.mkdir()
        mock_git.return_value = MagicMock(returncode=0, stdout="a" * 40 + "\n", stderr="")

        result = get_branch_sha(cache_path, "main")

        assert result == "a" * 40
        # First call should be for origin/main
        assert mock_git.call_args_list[0][0][0] == ["rev-parse", "origin/main"]

    @patch("skilz.git_ops.run_git_command")
    def test_falls_back_to_local_branch(self, mock_git, temp_dir):
        """Falls back to local branch if origin not found."""
        from skilz.git_ops import get_branch_sha

        cache_path = temp_dir / "repo"
        cache_path.mkdir()

        # First call fails, second succeeds
        mock_git.side_effect = [
            MagicMock(returncode=1, stdout="", stderr="error"),
            MagicMock(returncode=0, stdout="b" * 40 + "\n", stderr=""),
        ]

        result = get_branch_sha(cache_path, "develop")

        assert result == "b" * 40

    @patch("skilz.git_ops.run_git_command")
    def test_falls_back_to_origin_head(self, mock_git, temp_dir):
        """Falls back to origin/HEAD if branch not found."""
        from skilz.git_ops import get_branch_sha

        cache_path = temp_dir / "repo"
        cache_path.mkdir()

        # First two calls fail, third (origin/HEAD) succeeds
        mock_git.side_effect = [
            MagicMock(returncode=1, stdout="", stderr="error"),
            MagicMock(returncode=1, stdout="", stderr="error"),
            MagicMock(returncode=0, stdout="c" * 40 + "\n", stderr=""),
        ]

        result = get_branch_sha(cache_path, "nonexistent")

        assert result == "c" * 40

    @patch("skilz.git_ops.run_git_command")
    def test_falls_back_to_origin_main(self, mock_git, temp_dir):
        """Falls back to origin/main for non-main branches."""
        from skilz.git_ops import get_branch_sha

        cache_path = temp_dir / "repo"
        cache_path.mkdir()

        # All fail except origin/main
        mock_git.side_effect = [
            MagicMock(returncode=1, stdout="", stderr="error"),  # origin/develop
            MagicMock(returncode=1, stdout="", stderr="error"),  # develop
            MagicMock(returncode=1, stdout="", stderr="error"),  # origin/HEAD
            MagicMock(returncode=1, stdout="", stderr="error"),  # HEAD
            MagicMock(returncode=0, stdout="d" * 40 + "\n", stderr=""),  # origin/main
        ]

        result = get_branch_sha(cache_path, "develop")

        assert result == "d" * 40

    @patch("skilz.git_ops.run_git_command")
    def test_raises_error_when_all_fail(self, mock_git, temp_dir):
        """Raises GitError when no branch can be resolved."""
        from skilz.git_ops import get_branch_sha

        cache_path = temp_dir / "repo"
        cache_path.mkdir()

        # All calls fail
        mock_git.return_value = MagicMock(returncode=1, stdout="", stderr="error")

        with pytest.raises(GitError) as exc_info:
            get_branch_sha(cache_path, "nonexistent")

        assert "Could not resolve SHA" in str(exc_info.value)

    @patch("skilz.git_ops.run_git_command")
    def test_rejects_invalid_sha_length(self, mock_git, temp_dir):
        """Rejects SHA that isn't exactly 40 characters."""
        from skilz.git_ops import get_branch_sha

        cache_path = temp_dir / "repo"
        cache_path.mkdir()

        # Returns short SHA
        mock_git.return_value = MagicMock(returncode=0, stdout="abc123\n", stderr="")

        with pytest.raises(GitError):
            get_branch_sha(cache_path, "main")


class TestFindSkillByName:
    """Tests for find_skill_by_name function."""

    def test_finds_skill_by_directory_name(self, temp_dir):
        """Finds skill when directory name matches."""
        from skilz.git_ops import find_skill_by_name

        # Create skill structure
        skill_dir = temp_dir / "skills" / "my-skill"
        skill_dir.mkdir(parents=True)
        (skill_dir / "SKILL.md").write_text("# My Skill")

        result = find_skill_by_name(temp_dir, "my-skill")

        assert result == skill_dir

    def test_finds_skill_by_name_field(self, temp_dir):
        """Finds skill by name field in frontmatter."""
        from skilz.git_ops import find_skill_by_name

        # Create skill with different directory but matching name field
        skill_dir = temp_dir / "other-dir"
        skill_dir.mkdir(parents=True)
        (skill_dir / "SKILL.md").write_text("""---
name: target-skill
description: A skill
---
# Target Skill
""")

        result = find_skill_by_name(temp_dir, "target-skill")

        assert result == skill_dir

    def test_returns_none_when_not_found(self, temp_dir):
        """Returns None when skill not found."""
        from skilz.git_ops import find_skill_by_name

        result = find_skill_by_name(temp_dir, "nonexistent")

        assert result is None

    def test_ignores_git_directory(self, temp_dir):
        """Ignores SKILL.md files inside .git directory."""
        from skilz.git_ops import find_skill_by_name

        # Create skill inside .git (should be ignored)
        git_skill = temp_dir / ".git" / "hooks" / "my-skill"
        git_skill.mkdir(parents=True)
        (git_skill / "SKILL.md").write_text("# Should be ignored")

        result = find_skill_by_name(temp_dir, "my-skill")

        assert result is None

    def test_returns_first_match_when_multiple(self, temp_dir):
        """Returns first match when multiple skills have same name."""
        from skilz.git_ops import find_skill_by_name

        # Create multiple skills with same name
        skill1 = temp_dir / "dir1" / "dupe-skill"
        skill1.mkdir(parents=True)
        (skill1 / "SKILL.md").write_text("# Skill 1")

        skill2 = temp_dir / "dir2" / "dupe-skill"
        skill2.mkdir(parents=True)
        (skill2 / "SKILL.md").write_text("# Skill 2")

        result = find_skill_by_name(temp_dir, "dupe-skill")

        # Should return one of them (first found)
        assert result is not None
        assert result.name == "dupe-skill"


class TestFetchGithubSha:
    """Tests for fetch_github_sha function."""

    @patch("urllib.request.urlopen")
    def test_fetches_sha_successfully(self, mock_urlopen):
        """Fetches SHA from GitHub API."""
        from skilz.git_ops import fetch_github_sha

        mock_response = MagicMock()
        mock_response.read.return_value = b'{"sha": "' + b"a" * 40 + b'"}'
        mock_response.__enter__ = lambda s: mock_response
        mock_response.__exit__ = MagicMock(return_value=False)
        mock_urlopen.return_value = mock_response

        result = fetch_github_sha("owner", "repo", "main")

        assert result == "a" * 40

    @patch("urllib.request.urlopen")
    def test_raises_on_404(self, mock_urlopen):
        """Raises GitError on 404."""
        import urllib.error

        from skilz.git_ops import fetch_github_sha

        mock_urlopen.side_effect = urllib.error.HTTPError("url", 404, "Not Found", {}, None)

        with pytest.raises(GitError) as exc_info:
            fetch_github_sha("owner", "repo", "main")

        assert "not found" in str(exc_info.value).lower()

    @patch("urllib.request.urlopen")
    def test_raises_on_network_error(self, mock_urlopen):
        """Raises GitError on network error."""
        import urllib.error

        from skilz.git_ops import fetch_github_sha

        mock_urlopen.side_effect = urllib.error.URLError("Connection refused")

        with pytest.raises(GitError) as exc_info:
            fetch_github_sha("owner", "repo", "main")

        assert "Cannot connect" in str(exc_info.value)

    @patch("urllib.request.urlopen")
    def test_raises_on_invalid_json(self, mock_urlopen):
        """Raises GitError on invalid JSON response."""
        from skilz.git_ops import fetch_github_sha

        mock_response = MagicMock()
        mock_response.read.return_value = b"not json"
        mock_response.__enter__ = lambda s: mock_response
        mock_response.__exit__ = MagicMock(return_value=False)
        mock_urlopen.return_value = mock_response

        with pytest.raises(GitError) as exc_info:
            fetch_github_sha("owner", "repo", "main")

        assert "Invalid response" in str(exc_info.value)

    @patch("urllib.request.urlopen")
    def test_raises_on_invalid_sha(self, mock_urlopen):
        """Raises GitError when SHA is invalid."""
        from skilz.git_ops import fetch_github_sha

        mock_response = MagicMock()
        mock_response.read.return_value = b'{"sha": "short"}'
        mock_response.__enter__ = lambda s: mock_response
        mock_response.__exit__ = MagicMock(return_value=False)
        mock_urlopen.return_value = mock_response

        with pytest.raises(GitError) as exc_info:
            fetch_github_sha("owner", "repo", "main")

        assert "Invalid SHA" in str(exc_info.value)


class TestFetchGithubTagSha:
    """Tests for fetch_github_tag_sha function."""

    @patch("urllib.request.urlopen")
    def test_fetches_lightweight_tag(self, mock_urlopen):
        """Fetches SHA for lightweight tag."""
        from skilz.git_ops import fetch_github_tag_sha

        mock_response = MagicMock()
        mock_response.read.return_value = (
            b'{"object": {"type": "commit", "sha": "' + b"b" * 40 + b'"}}'
        )
        mock_response.__enter__ = lambda s: mock_response
        mock_response.__exit__ = MagicMock(return_value=False)
        mock_urlopen.return_value = mock_response

        result = fetch_github_tag_sha("owner", "repo", "v1.0.0")

        assert result == "b" * 40

    @patch("urllib.request.urlopen")
    def test_fetches_annotated_tag(self, mock_urlopen):
        """Fetches SHA for annotated tag (requires dereferencing)."""
        from skilz.git_ops import fetch_github_tag_sha

        # First call returns tag object, second dereferences to commit
        tag_response = MagicMock()
        tag_response.read.return_value = (
            b'{"object": {"type": "tag", "sha": "tag123", "url": "http://tag"}}'
        )
        tag_response.__enter__ = lambda s: tag_response
        tag_response.__exit__ = MagicMock(return_value=False)

        commit_response = MagicMock()
        commit_response.read.return_value = b'{"object": {"sha": "' + b"c" * 40 + b'"}}'
        commit_response.__enter__ = lambda s: commit_response
        commit_response.__exit__ = MagicMock(return_value=False)

        mock_urlopen.side_effect = [tag_response, commit_response]

        result = fetch_github_tag_sha("owner", "repo", "v1.0.0")

        assert result == "c" * 40

    @patch("urllib.request.urlopen")
    def test_tries_v_prefix(self, mock_urlopen):
        """Tries v-prefixed tag if plain tag not found."""
        import urllib.error

        from skilz.git_ops import fetch_github_tag_sha

        # First call (1.0.0) fails, second (v1.0.0) succeeds
        mock_response = MagicMock()
        mock_response.read.return_value = (
            b'{"object": {"type": "commit", "sha": "' + b"d" * 40 + b'"}}'
        )
        mock_response.__enter__ = lambda s: mock_response
        mock_response.__exit__ = MagicMock(return_value=False)

        mock_urlopen.side_effect = [
            urllib.error.HTTPError("url", 404, "Not Found", {}, None),
            mock_response,
        ]

        result = fetch_github_tag_sha("owner", "repo", "1.0.0")

        assert result == "d" * 40

    @patch("urllib.request.urlopen")
    def test_raises_when_tag_not_found(self, mock_urlopen):
        """Raises GitError when tag not found in any format."""
        import urllib.error

        from skilz.git_ops import fetch_github_tag_sha

        mock_urlopen.side_effect = urllib.error.HTTPError("url", 404, "Not Found", {}, None)

        with pytest.raises(GitError) as exc_info:
            fetch_github_tag_sha("owner", "repo", "nonexistent")

        assert "Tag not found" in str(exc_info.value)


class TestResolveVersionSpec:
    """Tests for resolve_version_spec function."""

    def test_none_returns_default(self):
        """None version spec returns default SHA."""
        from skilz.git_ops import resolve_version_spec

        result = resolve_version_spec("owner", "repo", None, "default123")

        assert result == "default123"

    @patch("skilz.git_ops.fetch_github_sha")
    def test_latest_fetches_main(self, mock_fetch):
        """'latest' fetches from main branch."""
        from skilz.git_ops import resolve_version_spec

        mock_fetch.return_value = "e" * 40

        result = resolve_version_spec("owner", "repo", "latest", "default")

        mock_fetch.assert_called_once_with("owner", "repo", "main", verbose=False)
        assert result == "e" * 40

    @patch("skilz.git_ops.fetch_github_sha")
    def test_latest_case_insensitive(self, mock_fetch):
        """'LATEST' (uppercase) works same as 'latest'."""
        from skilz.git_ops import resolve_version_spec

        mock_fetch.return_value = "f" * 40

        result = resolve_version_spec("owner", "repo", "LATEST", "default")

        mock_fetch.assert_called_once()
        assert result == "f" * 40

    @patch("skilz.git_ops.fetch_github_sha")
    def test_branch_prefix(self, mock_fetch):
        """'branch:NAME' fetches from specified branch."""
        from skilz.git_ops import resolve_version_spec

        mock_fetch.return_value = "g" * 40

        result = resolve_version_spec("owner", "repo", "branch:develop", "default")

        mock_fetch.assert_called_once_with("owner", "repo", "develop", verbose=False)
        assert result == "g" * 40

    def test_full_sha_returned_as_is(self):
        """40-character hex string returned as-is."""
        from skilz.git_ops import resolve_version_spec

        full_sha = "a1b2c3d4e5" * 4  # 40 chars

        result = resolve_version_spec("owner", "repo", full_sha, "default")

        assert result == full_sha.lower()

    def test_short_sha_returned_as_is(self):
        """Short SHA (7-39 chars) returned as-is."""
        from skilz.git_ops import resolve_version_spec

        short_sha = "abc1234"  # 7 chars

        result = resolve_version_spec("owner", "repo", short_sha, "default")

        assert result == short_sha.lower()

    @patch("skilz.git_ops.fetch_github_tag_sha")
    def test_tag_resolution(self, mock_fetch):
        """Non-SHA, non-keyword treated as tag."""
        from skilz.git_ops import resolve_version_spec

        mock_fetch.return_value = "h" * 40

        result = resolve_version_spec("owner", "repo", "v1.0.0", "default")

        mock_fetch.assert_called_once_with("owner", "repo", "v1.0.0", verbose=False)
        assert result == "h" * 40
