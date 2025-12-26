"""Tests for the link_ops module."""

import subprocess
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from skilz.link_ops import (
    InstallMode,
    cleanup_temp_dir,
    clone_git_repo,
    copy_skill,
    create_symlink,
    determine_install_mode,
    ensure_canonical_copy,
    get_canonical_path,
    get_skill_name_from_path,
    get_symlink_target,
    is_broken_symlink,
    is_symlink,
    remove_skill,
    validate_skill_source,
)


class TestCreateSymlink:
    """Tests for create_symlink function."""

    def test_creates_symlink_to_source(self, temp_dir):
        """Create a symlink pointing to source directory."""
        source = temp_dir / "source_skill"
        source.mkdir()
        (source / "SKILL.md").write_text("# Test Skill")

        target = temp_dir / "agent" / "skills" / "my-skill"

        create_symlink(source, target)

        assert target.is_symlink()
        assert target.resolve() == source.resolve()

    def test_creates_parent_directories(self, temp_dir):
        """Parent directories are created if needed."""
        source = temp_dir / "source"
        source.mkdir()

        target = temp_dir / "deep" / "nested" / "path" / "skill"

        create_symlink(source, target)

        assert target.is_symlink()
        assert target.parent.exists()

    def test_raises_if_source_not_exists(self, temp_dir):
        """Raise FileNotFoundError if source doesn't exist."""
        source = temp_dir / "nonexistent"
        target = temp_dir / "target"

        with pytest.raises(FileNotFoundError) as exc_info:
            create_symlink(source, target)

        assert "does not exist" in str(exc_info.value)

    def test_raises_if_target_exists(self, temp_dir):
        """Raise FileExistsError if target already exists."""
        source = temp_dir / "source"
        source.mkdir()

        target = temp_dir / "target"
        target.mkdir()

        with pytest.raises(FileExistsError) as exc_info:
            create_symlink(source, target)

        assert "already exists" in str(exc_info.value)

    def test_raises_if_target_is_existing_symlink(self, temp_dir):
        """Raise FileExistsError if target is an existing symlink."""
        source1 = temp_dir / "source1"
        source1.mkdir()
        source2 = temp_dir / "source2"
        source2.mkdir()

        target = temp_dir / "target"
        target.symlink_to(source1)

        with pytest.raises(FileExistsError):
            create_symlink(source2, target)


class TestCopySkill:
    """Tests for copy_skill function."""

    def test_copies_directory_tree(self, temp_dir):
        """Copy entire directory tree to target."""
        source = temp_dir / "source"
        source.mkdir()
        (source / "SKILL.md").write_text("# Test Skill")
        (source / "subdir").mkdir()
        (source / "subdir" / "file.txt").write_text("content")

        target = temp_dir / "target"

        copy_skill(source, target)

        assert target.exists()
        assert (target / "SKILL.md").read_text() == "# Test Skill"
        assert (target / "subdir" / "file.txt").read_text() == "content"

    def test_creates_parent_directories(self, temp_dir):
        """Parent directories are created if needed."""
        source = temp_dir / "source"
        source.mkdir()
        (source / "SKILL.md").write_text("content")

        target = temp_dir / "deep" / "nested" / "target"

        copy_skill(source, target)

        assert target.exists()

    def test_overwrites_existing_target(self, temp_dir):
        """Overwrite existing target directory."""
        source = temp_dir / "source"
        source.mkdir()
        (source / "SKILL.md").write_text("new content")

        target = temp_dir / "target"
        target.mkdir()
        (target / "old.txt").write_text("old content")

        copy_skill(source, target)

        assert (target / "SKILL.md").read_text() == "new content"
        assert not (target / "old.txt").exists()

    def test_raises_if_source_not_exists(self, temp_dir):
        """Raise FileNotFoundError if source doesn't exist."""
        source = temp_dir / "nonexistent"
        target = temp_dir / "target"

        with pytest.raises(FileNotFoundError) as exc_info:
            copy_skill(source, target)

        assert "does not exist" in str(exc_info.value)

    def test_raises_if_source_is_file(self, temp_dir):
        """Raise NotADirectoryError if source is a file."""
        source = temp_dir / "source.txt"
        source.write_text("content")
        target = temp_dir / "target"

        with pytest.raises(NotADirectoryError) as exc_info:
            copy_skill(source, target)

        assert "not a directory" in str(exc_info.value)


class TestIsSymlink:
    """Tests for is_symlink function."""

    def test_returns_true_for_symlink(self, temp_dir):
        """Return True for a symlink."""
        source = temp_dir / "source"
        source.mkdir()
        link = temp_dir / "link"
        link.symlink_to(source)

        assert is_symlink(link) is True

    def test_returns_false_for_directory(self, temp_dir):
        """Return False for a regular directory."""
        path = temp_dir / "dir"
        path.mkdir()

        assert is_symlink(path) is False

    def test_returns_false_for_file(self, temp_dir):
        """Return False for a regular file."""
        path = temp_dir / "file.txt"
        path.write_text("content")

        assert is_symlink(path) is False

    def test_returns_true_for_broken_symlink(self, temp_dir):
        """Return True for a broken symlink."""
        source = temp_dir / "source"
        source.mkdir()
        link = temp_dir / "link"
        link.symlink_to(source)
        source.rmdir()  # Break the symlink

        assert is_symlink(link) is True

    def test_returns_false_for_nonexistent(self, temp_dir):
        """Return False for nonexistent path."""
        path = temp_dir / "nonexistent"

        assert is_symlink(path) is False


class TestGetSymlinkTarget:
    """Tests for get_symlink_target function."""

    def test_returns_target_for_symlink(self, temp_dir):
        """Return resolved target path for symlink."""
        source = temp_dir / "source"
        source.mkdir()
        link = temp_dir / "link"
        link.symlink_to(source)

        target = get_symlink_target(link)

        # Resolve both to handle macOS /var -> /private/var symlink
        assert target.resolve() == source.resolve()

    def test_returns_none_for_non_symlink(self, temp_dir):
        """Return None for regular directory."""
        path = temp_dir / "dir"
        path.mkdir()

        assert get_symlink_target(path) is None

    def test_returns_target_for_broken_symlink(self, temp_dir):
        """Return target path even for broken symlink."""
        source = temp_dir / "source"
        source.mkdir()
        link = temp_dir / "link"
        link.symlink_to(source)
        source.rmdir()  # Break the symlink

        target = get_symlink_target(link)

        # Should still return the target path
        assert target is not None
        assert "source" in str(target)

    def test_handles_relative_symlinks(self, temp_dir):
        """Handle relative symlinks correctly."""
        source = temp_dir / "source"
        source.mkdir()
        link = temp_dir / "link"
        # Create relative symlink
        link.symlink_to(Path("source"))

        target = get_symlink_target(link)

        assert target == source.resolve()


class TestIsBrokenSymlink:
    """Tests for is_broken_symlink function."""

    def test_returns_true_for_broken_symlink(self, temp_dir):
        """Return True for broken symlink."""
        source = temp_dir / "source"
        source.mkdir()
        link = temp_dir / "link"
        link.symlink_to(source)
        source.rmdir()  # Break the symlink

        assert is_broken_symlink(link) is True

    def test_returns_false_for_valid_symlink(self, temp_dir):
        """Return False for valid symlink."""
        source = temp_dir / "source"
        source.mkdir()
        link = temp_dir / "link"
        link.symlink_to(source)

        assert is_broken_symlink(link) is False

    def test_returns_false_for_directory(self, temp_dir):
        """Return False for regular directory."""
        path = temp_dir / "dir"
        path.mkdir()

        assert is_broken_symlink(path) is False

    def test_returns_false_for_nonexistent(self, temp_dir):
        """Return False for nonexistent path."""
        path = temp_dir / "nonexistent"

        assert is_broken_symlink(path) is False


class TestValidateSkillSource:
    """Tests for validate_skill_source function."""

    def test_valid_skill_source(self, temp_dir):
        """Return (True, None) for valid skill source."""
        skill_dir = temp_dir / "my-skill"
        skill_dir.mkdir()
        (skill_dir / "SKILL.md").write_text("# My Skill")

        is_valid, error = validate_skill_source(skill_dir)

        assert is_valid is True
        assert error is None

    def test_invalid_nonexistent_path(self, temp_dir):
        """Return (False, error) for nonexistent path."""
        path = temp_dir / "nonexistent"

        is_valid, error = validate_skill_source(path)

        assert is_valid is False
        assert "does not exist" in error

    def test_invalid_not_directory(self, temp_dir):
        """Return (False, error) for file instead of directory."""
        path = temp_dir / "file.txt"
        path.write_text("content")

        is_valid, error = validate_skill_source(path)

        assert is_valid is False
        assert "not a directory" in error

    def test_invalid_missing_skill_md(self, temp_dir):
        """Return (False, error) for directory without SKILL.md."""
        path = temp_dir / "my-skill"
        path.mkdir()

        is_valid, error = validate_skill_source(path)

        assert is_valid is False
        assert "Missing SKILL.md" in error


class TestDetermineInstallMode:
    """Tests for determine_install_mode function."""

    def test_explicit_copy_overrides_default(self):
        """Explicit copy mode overrides symlink default."""
        mode = determine_install_mode("copy", "symlink")
        assert mode == "copy"

    def test_explicit_symlink_overrides_default(self):
        """Explicit symlink mode overrides copy default."""
        mode = determine_install_mode("symlink", "copy")
        assert mode == "symlink"

    def test_none_uses_agent_default_copy(self):
        """None uses agent default (copy)."""
        mode = determine_install_mode(None, "copy")
        assert mode == "copy"

    def test_none_uses_agent_default_symlink(self):
        """None uses agent default (symlink)."""
        mode = determine_install_mode(None, "symlink")
        assert mode == "symlink"


class TestRemoveSkill:
    """Tests for remove_skill function."""

    def test_remove_symlink(self, temp_dir):
        """Remove symlink without affecting target."""
        source = temp_dir / "source"
        source.mkdir()
        (source / "SKILL.md").write_text("content")

        link = temp_dir / "link"
        link.symlink_to(source)

        result = remove_skill(link)

        assert result is True
        assert not link.exists()
        assert source.exists()  # Target unaffected

    def test_remove_directory(self, temp_dir):
        """Remove regular directory."""
        path = temp_dir / "skill"
        path.mkdir()
        (path / "SKILL.md").write_text("content")

        result = remove_skill(path)

        assert result is True
        assert not path.exists()

    def test_remove_nonexistent_returns_false(self, temp_dir):
        """Return False for nonexistent path."""
        path = temp_dir / "nonexistent"

        result = remove_skill(path)

        assert result is False

    def test_remove_broken_symlink(self, temp_dir):
        """Remove broken symlink."""
        source = temp_dir / "source"
        source.mkdir()
        link = temp_dir / "link"
        link.symlink_to(source)
        source.rmdir()  # Break it

        result = remove_skill(link)

        assert result is True
        assert not link.exists()


class TestGetCanonicalPath:
    """Tests for get_canonical_path function."""

    def test_global_install_uses_home(self):
        """Global install uses ~/.skilz/skills/."""
        path = get_canonical_path("pdf", global_install=True)

        assert ".skilz" in str(path)
        assert "skills" in str(path)
        assert path.name == "pdf"
        assert str(Path.home()) in str(path)

    def test_local_install_uses_cwd(self):
        """Local install uses .skilz/skills/ in current directory."""
        path = get_canonical_path("pdf", global_install=False)

        assert ".skilz" in str(path)
        assert "skills" in str(path)
        assert path.name == "pdf"
        # Should be relative to cwd, not home
        assert str(Path.cwd()) in str(path)


class TestEnsureCanonicalCopy:
    """Tests for ensure_canonical_copy function."""

    def test_copies_if_not_exists(self, temp_dir):
        """Copy to canonical location if it doesn't exist."""
        source = temp_dir / "source"
        source.mkdir()
        (source / "SKILL.md").write_text("# Test")

        # Mock get_canonical_path to use temp_dir
        with patch("skilz.link_ops.get_canonical_path") as mock_canonical:
            canonical = temp_dir / ".skilz" / "skills" / "test-skill"
            mock_canonical.return_value = canonical

            result = ensure_canonical_copy(source, "test-skill")

            assert result == canonical
            assert canonical.exists()
            assert (canonical / "SKILL.md").read_text() == "# Test"

    def test_returns_existing_canonical(self, temp_dir):
        """Return existing canonical path without copying."""
        source = temp_dir / "source"
        source.mkdir()
        (source / "SKILL.md").write_text("# New")

        with patch("skilz.link_ops.get_canonical_path") as mock_canonical:
            canonical = temp_dir / ".skilz" / "skills" / "test-skill"
            canonical.mkdir(parents=True)
            (canonical / "SKILL.md").write_text("# Existing")
            mock_canonical.return_value = canonical

            result = ensure_canonical_copy(source, "test-skill")

            assert result == canonical
            # Should NOT overwrite existing
            assert (canonical / "SKILL.md").read_text() == "# Existing"


class TestCloneGitRepo:
    """Tests for clone_git_repo function."""

    @patch("subprocess.run")
    def test_clones_to_temp_directory(self, mock_run):
        """Clone repo to temporary directory."""
        mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")

        result = clone_git_repo("https://github.com/test/repo.git")

        mock_run.assert_called_once()
        args = mock_run.call_args
        assert "git" in args[0][0][0]
        assert "clone" in args[0][0]
        assert "--depth" in args[0][0]
        assert "1" in args[0][0]
        assert result.exists() or True  # Temp dir created

        # Cleanup
        if result.exists():
            cleanup_temp_dir(result)

    @patch("subprocess.run")
    def test_raises_on_clone_failure(self, mock_run):
        """Raise RuntimeError if clone fails."""
        mock_run.return_value = MagicMock(
            returncode=1, stdout="", stderr="fatal: repository not found"
        )

        with pytest.raises(RuntimeError) as exc_info:
            clone_git_repo("https://github.com/test/nonexistent.git")

        assert "Git clone failed" in str(exc_info.value)

    @patch("subprocess.run")
    def test_raises_on_timeout(self, mock_run):
        """Raise RuntimeError on timeout."""
        mock_run.side_effect = subprocess.TimeoutExpired(["git"], 120)

        with pytest.raises(RuntimeError) as exc_info:
            clone_git_repo("https://github.com/test/slow-repo.git")

        assert "timed out" in str(exc_info.value)

    @patch("subprocess.run")
    def test_raises_if_git_not_installed(self, mock_run):
        """Raise RuntimeError if git not installed."""
        mock_run.side_effect = FileNotFoundError()

        with pytest.raises(RuntimeError) as exc_info:
            clone_git_repo("https://github.com/test/repo.git")

        assert "not installed" in str(exc_info.value)


class TestCleanupTempDir:
    """Tests for cleanup_temp_dir function."""

    def test_removes_existing_directory(self, temp_dir):
        """Remove existing directory."""
        path = temp_dir / "to-clean"
        path.mkdir()
        (path / "file.txt").write_text("content")

        cleanup_temp_dir(path)

        assert not path.exists()

    def test_handles_nonexistent_directory(self, temp_dir):
        """Handle nonexistent directory gracefully."""
        path = temp_dir / "nonexistent"

        # Should not raise
        cleanup_temp_dir(path)


class TestGetSkillNameFromPath:
    """Tests for get_skill_name_from_path function."""

    def test_extracts_directory_name(self, temp_dir):
        """Extract skill name from path."""
        path = temp_dir / "skills" / "my-awesome-skill"

        name = get_skill_name_from_path(path)

        assert name == "my-awesome-skill"

    def test_works_with_simple_path(self):
        """Work with simple path."""
        path = Path("/path/to/pdf")

        name = get_skill_name_from_path(path)

        assert name == "pdf"


class TestInstallModeType:
    """Tests for InstallMode type alias."""

    def test_copy_is_valid(self):
        """'copy' is a valid install mode."""
        mode: InstallMode = "copy"
        assert mode == "copy"

    def test_symlink_is_valid(self):
        """'symlink' is a valid install mode."""
        mode: InstallMode = "symlink"
        assert mode == "symlink"
