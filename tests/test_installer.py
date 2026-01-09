"""Tests for the installer module."""

from unittest.mock import patch

import pytest

from skilz.errors import InstallError
from skilz.installer import copy_skill_files, install_local_skill, install_skill
from skilz.registry import SkillInfo


class TestCopySkillFiles:
    """Tests for copy_skill_files function."""

    def test_copy_files_success(self, temp_dir):
        """Test successful file copy."""
        source = temp_dir / "source"
        source.mkdir()
        (source / "SKILL.md").write_text("# Test Skill")
        (source / "subdir").mkdir()
        (source / "subdir" / "file.txt").write_text("content")

        target = temp_dir / "target"

        copy_skill_files(source, target, verbose=False)

        assert target.exists()
        assert (target / "SKILL.md").exists()
        assert (target / "SKILL.md").read_text() == "# Test Skill"
        assert (target / "subdir" / "file.txt").exists()
        assert (target / "subdir" / "file.txt").read_text() == "content"

    def test_copy_source_not_exists(self, temp_dir):
        """Test error when source doesn't exist."""
        source = temp_dir / "nonexistent"
        target = temp_dir / "target"

        with pytest.raises(InstallError) as exc:
            copy_skill_files(source, target)

        assert "does not exist" in str(exc.value)

    def test_copy_source_not_directory(self, temp_dir):
        """Test error when source is a file."""
        source = temp_dir / "source_file"
        source.write_text("not a directory")
        target = temp_dir / "target"

        with pytest.raises(InstallError) as exc:
            copy_skill_files(source, target)

        assert "not a directory" in str(exc.value)

    def test_copy_replaces_existing(self, temp_dir):
        """Test that existing target is replaced."""
        source = temp_dir / "source"
        source.mkdir()
        (source / "new.txt").write_text("new content")

        target = temp_dir / "target"
        target.mkdir()
        (target / "old.txt").write_text("old content")

        copy_skill_files(source, target, verbose=False)

        assert (target / "new.txt").exists()
        assert (target / "new.txt").read_text() == "new content"
        assert not (target / "old.txt").exists()

    def test_copy_verbose_output(self, temp_dir, capsys):
        """Test verbose output during copy."""
        source = temp_dir / "source"
        source.mkdir()
        (source / "SKILL.md").write_text("# Test")

        target = temp_dir / "target"

        copy_skill_files(source, target, verbose=True)

        captured = capsys.readouterr()
        assert "Copying" in captured.out

    def test_copy_verbose_removes_existing(self, temp_dir, capsys):
        """Test verbose output when removing existing target."""
        source = temp_dir / "source"
        source.mkdir()
        (source / "SKILL.md").write_text("# Test")

        target = temp_dir / "target"
        target.mkdir()
        (target / "old.txt").write_text("old")

        copy_skill_files(source, target, verbose=True)

        captured = capsys.readouterr()
        assert "Removing existing" in captured.out

    def test_copy_creates_parent_directory(self, temp_dir):
        """Test that parent directories are created."""
        source = temp_dir / "source"
        source.mkdir()
        (source / "SKILL.md").write_text("# Test")

        target = temp_dir / "deep" / "nested" / "target"

        copy_skill_files(source, target, verbose=False)

        assert target.exists()
        assert (target / "SKILL.md").exists()


class TestInstallLocalSkill:
    """Tests for install_local_skill function."""

    def test_install_local_success(self, temp_dir):
        """Test successful local installation."""
        source = temp_dir / "my-skill"
        source.mkdir()
        (source / "SKILL.md").write_text("# My Skill")

        target_root = temp_dir / ".claude" / "skills"
        target_root.mkdir(parents=True)

        with (
            patch("skilz.installer.detect_agent", return_value="claude"),
            patch("skilz.installer.ensure_skills_dir", return_value=target_root),
            patch("skilz.installer.write_manifest") as mock_write,
        ):
            install_local_skill(source, project_level=True)

            assert (target_root / "my-skill").exists()
            assert (target_root / "my-skill" / "SKILL.md").read_text() == "# My Skill"

            mock_write.assert_called_once()
            manifest = mock_write.call_args[0][1]
            assert manifest.skill_id == "local/my-skill"
            assert manifest.install_mode == "copy"

    def test_install_local_not_found(self, temp_dir):
        """Test error when local source does not exist."""
        source = temp_dir / "nonexistent"

        with pytest.raises(InstallError) as exc:
            install_local_skill(source)

        assert "does not exist" in str(exc.value)

    def test_install_local_not_dir(self, temp_dir):
        """Test error when source is a file."""
        source = temp_dir / "file"
        source.write_text("content")

        with pytest.raises(InstallError) as exc:
            install_local_skill(source)

        assert "not a directory" in str(exc.value)


class TestInstallSkill:
    """Tests for install_skill function."""

    @pytest.fixture
    def mock_skill_info(self):
        """Create a mock SkillInfo for testing."""
        return SkillInfo(
            skill_id="test/skill",
            git_repo="https://github.com/test/repo.git",
            skill_path="/main/skills/test-skill",
            git_sha="abc123def456789012345678901234567890abcd",
        )

    @pytest.fixture
    def mock_dependencies(self, temp_dir, mock_skill_info):
        """Set up common mocks for install_skill."""
        cache_path = temp_dir / "cache" / "repo"
        cache_path.mkdir(parents=True)

        source_path = cache_path / "skills" / "test-skill"
        source_path.mkdir(parents=True)
        (source_path / "SKILL.md").write_text("# Test Skill")

        skills_dir = temp_dir / ".claude" / "skills"
        skills_dir.mkdir(parents=True)

        return {
            "cache_path": cache_path,
            "source_path": source_path,
            "skills_dir": skills_dir,
            "skill_info": mock_skill_info,
        }

    def test_install_new_skill(self, mock_dependencies):
        """Test installing a new skill."""
        deps = mock_dependencies

        with (
            patch("skilz.installer.detect_agent", return_value="claude"),
            patch("skilz.installer.get_agent_display_name", return_value="Claude Code"),
            patch("skilz.installer.lookup_skill", return_value=deps["skill_info"]),
            patch("skilz.installer.ensure_skills_dir", return_value=deps["skills_dir"]),
            patch("skilz.installer.needs_install", return_value=(True, "not_installed")),
            patch("skilz.installer.clone_or_fetch", return_value=deps["cache_path"]),
            patch("skilz.installer.parse_skill_path", return_value=("main", "skills/test-skill")),
            patch("skilz.installer.checkout_sha"),
            patch("skilz.installer.get_skill_source_path", return_value=deps["source_path"]),
            patch("skilz.installer.write_manifest"),
        ):
            install_skill("test/skill", project_level=True)

    def test_install_already_installed(self, mock_dependencies, capsys):
        """Test when skill is already installed."""
        deps = mock_dependencies

        with (
            patch("skilz.installer.detect_agent", return_value="claude"),
            patch("skilz.installer.get_agent_display_name", return_value="Claude Code"),
            patch("skilz.installer.lookup_skill", return_value=deps["skill_info"]),
            patch("skilz.installer.ensure_skills_dir", return_value=deps["skills_dir"]),
            patch("skilz.installer.needs_install", return_value=(False, "up_to_date")),
        ):
            install_skill("test/skill", project_level=True)

        captured = capsys.readouterr()
        assert "Already installed" in captured.out

    def test_install_update_existing(self, mock_dependencies, capsys):
        """Test updating an existing skill."""
        deps = mock_dependencies

        with (
            patch("skilz.installer.detect_agent", return_value="claude"),
            patch("skilz.installer.get_agent_display_name", return_value="Claude Code"),
            patch("skilz.installer.lookup_skill", return_value=deps["skill_info"]),
            patch("skilz.installer.ensure_skills_dir", return_value=deps["skills_dir"]),
            patch("skilz.installer.needs_install", return_value=(True, "sha_mismatch")),
            patch("skilz.installer.clone_or_fetch", return_value=deps["cache_path"]),
            patch("skilz.installer.parse_skill_path", return_value=("main", "skills/test-skill")),
            patch("skilz.installer.checkout_sha"),
            patch("skilz.installer.get_skill_source_path", return_value=deps["source_path"]),
            patch("skilz.installer.write_manifest"),
        ):
            install_skill("test/skill", project_level=True)

        captured = capsys.readouterr()
        assert "Updated" in captured.out

    def test_install_source_not_found(self, temp_dir, mock_dependencies):
        """Test error when skill source path doesn't exist and fallback search fails."""
        deps = mock_dependencies
        nonexistent = temp_dir / "nonexistent"

        with (
            patch("skilz.installer.detect_agent", return_value="claude"),
            patch("skilz.installer.get_agent_display_name", return_value="Claude Code"),
            patch("skilz.installer.lookup_skill", return_value=deps["skill_info"]),
            patch("skilz.installer.ensure_skills_dir", return_value=deps["skills_dir"]),
            patch("skilz.installer.needs_install", return_value=(True, "not_installed")),
            patch("skilz.installer.clone_or_fetch", return_value=deps["cache_path"]),
            patch("skilz.installer.parse_skill_path", return_value=("main", "skills/test-skill")),
            patch("skilz.installer.checkout_sha"),
            patch("skilz.installer.get_skill_source_path", return_value=nonexistent),
            patch("skilz.installer.find_skill_by_name", return_value=None),
        ):
            with pytest.raises(InstallError) as exc:
                install_skill("test/skill", project_level=True)

            assert "not found in repository" in str(exc.value)

    def test_install_with_explicit_agent(self, mock_dependencies, capsys):
        """Test installing with explicitly specified agent."""
        deps = mock_dependencies

        with (
            patch("skilz.installer.get_agent_display_name", return_value="OpenCode"),
            patch("skilz.installer.lookup_skill", return_value=deps["skill_info"]),
            patch("skilz.installer.ensure_skills_dir", return_value=deps["skills_dir"]),
            patch("skilz.installer.needs_install", return_value=(True, "not_installed")),
            patch("skilz.installer.clone_or_fetch", return_value=deps["cache_path"]),
            patch("skilz.installer.parse_skill_path", return_value=("main", "skills/test-skill")),
            patch("skilz.installer.checkout_sha"),
            patch("skilz.installer.get_skill_source_path", return_value=deps["source_path"]),
            patch("skilz.installer.write_manifest"),
        ):
            # Note: detect_agent is NOT called because agent is explicit
            install_skill("test/skill", agent="opencode", project_level=True)

        captured = capsys.readouterr()
        assert "Installed" in captured.out

    def test_install_verbose_output(self, mock_dependencies, capsys):
        """Test verbose output during installation."""
        deps = mock_dependencies

        with (
            patch("skilz.installer.detect_agent", return_value="claude"),
            patch("skilz.installer.get_agent_display_name", return_value="Claude Code"),
            patch("skilz.installer.lookup_skill", return_value=deps["skill_info"]),
            patch("skilz.installer.ensure_skills_dir", return_value=deps["skills_dir"]),
            patch("skilz.installer.needs_install", return_value=(True, "not_installed")),
            patch("skilz.installer.clone_or_fetch", return_value=deps["cache_path"]),
            patch("skilz.installer.parse_skill_path", return_value=("main", "skills/test-skill")),
            patch("skilz.installer.checkout_sha"),
            patch("skilz.installer.get_skill_source_path", return_value=deps["source_path"]),
            patch("skilz.installer.write_manifest"),
        ):
            install_skill("test/skill", project_level=True, verbose=True)

        captured = capsys.readouterr()
        assert "Auto-detected agent" in captured.out
        assert "Looking up skill" in captured.out

    def test_install_verbose_sha_mismatch(self, mock_dependencies, capsys):
        """Test verbose output for SHA mismatch update."""
        deps = mock_dependencies

        with (
            patch("skilz.installer.detect_agent", return_value="claude"),
            patch("skilz.installer.get_agent_display_name", return_value="Claude Code"),
            patch("skilz.installer.lookup_skill", return_value=deps["skill_info"]),
            patch("skilz.installer.ensure_skills_dir", return_value=deps["skills_dir"]),
            patch("skilz.installer.needs_install", return_value=(True, "sha_mismatch")),
            patch("skilz.installer.clone_or_fetch", return_value=deps["cache_path"]),
            patch("skilz.installer.parse_skill_path", return_value=("main", "skills/test-skill")),
            patch("skilz.installer.checkout_sha"),
            patch("skilz.installer.get_skill_source_path", return_value=deps["source_path"]),
            patch("skilz.installer.write_manifest"),
        ):
            install_skill("test/skill", project_level=True, verbose=True)

        captured = capsys.readouterr()
        assert "Updating" in captured.out or "SHA changed" in captured.out

    def test_install_verbose_no_manifest(self, mock_dependencies, capsys):
        """Test verbose output for no manifest reinstall."""
        deps = mock_dependencies

        with (
            patch("skilz.installer.detect_agent", return_value="claude"),
            patch("skilz.installer.get_agent_display_name", return_value="Claude Code"),
            patch("skilz.installer.lookup_skill", return_value=deps["skill_info"]),
            patch("skilz.installer.ensure_skills_dir", return_value=deps["skills_dir"]),
            patch("skilz.installer.needs_install", return_value=(True, "no_manifest")),
            patch("skilz.installer.clone_or_fetch", return_value=deps["cache_path"]),
            patch("skilz.installer.parse_skill_path", return_value=("main", "skills/test-skill")),
            patch("skilz.installer.checkout_sha"),
            patch("skilz.installer.get_skill_source_path", return_value=deps["source_path"]),
            patch("skilz.installer.write_manifest"),
        ):
            install_skill("test/skill", project_level=True, verbose=True)

        captured = capsys.readouterr()
        assert "Reinstalling" in captured.out or "no manifest" in captured.out

    def test_install_user_level(self, mock_dependencies, capsys):
        """Test user-level installation."""
        deps = mock_dependencies

        with (
            patch("skilz.installer.detect_agent", return_value="claude"),
            patch("skilz.installer.get_agent_display_name", return_value="Claude Code"),
            patch("skilz.installer.lookup_skill", return_value=deps["skill_info"]),
            patch("skilz.installer.ensure_skills_dir", return_value=deps["skills_dir"]),
            patch("skilz.installer.needs_install", return_value=(True, "not_installed")),
            patch("skilz.installer.clone_or_fetch", return_value=deps["cache_path"]),
            patch("skilz.installer.parse_skill_path", return_value=("main", "skills/test-skill")),
            patch("skilz.installer.checkout_sha"),
            patch("skilz.installer.get_skill_source_path", return_value=deps["source_path"]),
            patch("skilz.installer.write_manifest"),
        ):
            install_skill("test/skill", project_level=False)

        captured = capsys.readouterr()
        assert "user" in captured.out

    def test_install_writes_manifest(self, mock_dependencies):
        """Test that manifest is written after installation."""
        deps = mock_dependencies

        with (
            patch("skilz.installer.detect_agent", return_value="claude"),
            patch("skilz.installer.get_agent_display_name", return_value="Claude Code"),
            patch("skilz.installer.lookup_skill", return_value=deps["skill_info"]),
            patch("skilz.installer.ensure_skills_dir", return_value=deps["skills_dir"]),
            patch("skilz.installer.needs_install", return_value=(True, "not_installed")),
            patch("skilz.installer.clone_or_fetch", return_value=deps["cache_path"]),
            patch("skilz.installer.parse_skill_path", return_value=("main", "skills/test-skill")),
            patch("skilz.installer.checkout_sha"),
            patch("skilz.installer.get_skill_source_path", return_value=deps["source_path"]),
            patch("skilz.installer.write_manifest") as mock_write,
        ):
            install_skill("test/skill", project_level=True)

            mock_write.assert_called_once()
            args = mock_write.call_args
            manifest = args[0][1]
            assert manifest.skill_id == "test/skill"
            assert manifest.git_sha == deps["skill_info"].git_sha


class TestInstallMode:
    """Tests for install mode (copy vs symlink) support."""

    @pytest.fixture
    def mock_skill_info(self):
        """Create a mock SkillInfo for testing."""
        return SkillInfo(
            skill_id="test/skill",
            git_repo="https://github.com/test/repo.git",
            skill_path="/main/skills/test-skill",
            git_sha="abc123def456789012345678901234567890abcd",
        )

    @pytest.fixture
    def mock_dependencies(self, temp_dir, mock_skill_info):
        """Set up common mocks for install_skill."""
        cache_path = temp_dir / "cache" / "repo"
        cache_path.mkdir(parents=True)

        source_path = cache_path / "skills" / "test-skill"
        source_path.mkdir(parents=True)
        (source_path / "SKILL.md").write_text("# Test Skill")

        skills_dir = temp_dir / ".claude" / "skills"
        skills_dir.mkdir(parents=True)

        return {
            "cache_path": cache_path,
            "source_path": source_path,
            "skills_dir": skills_dir,
            "skill_info": mock_skill_info,
            "temp_dir": temp_dir,
        }

    def test_install_with_explicit_copy_mode(self, mock_dependencies, capsys):
        """Test installing with explicit copy mode."""
        deps = mock_dependencies

        with (
            patch("skilz.installer.detect_agent", return_value="claude"),
            patch("skilz.installer.get_agent_display_name", return_value="Claude Code"),
            patch("skilz.installer.get_agent_default_mode", return_value="symlink"),
            patch("skilz.installer.lookup_skill", return_value=deps["skill_info"]),
            patch("skilz.installer.ensure_skills_dir", return_value=deps["skills_dir"]),
            patch("skilz.installer.needs_install", return_value=(True, "not_installed")),
            patch("skilz.installer.clone_or_fetch", return_value=deps["cache_path"]),
            patch("skilz.installer.parse_skill_path", return_value=("main", "skills/test-skill")),
            patch("skilz.installer.checkout_sha"),
            patch("skilz.installer.get_skill_source_path", return_value=deps["source_path"]),
            patch("skilz.installer.write_manifest") as mock_write,
        ):
            # Explicit mode="copy" should override agent default
            install_skill("test/skill", project_level=True, mode="copy")

            # Verify manifest has install_mode="copy"
            mock_write.assert_called_once()
            manifest = mock_write.call_args[0][1]
            assert manifest.install_mode == "copy"

    def test_install_with_explicit_symlink_mode(self, mock_dependencies, capsys):
        """Test installing with explicit symlink mode."""
        deps = mock_dependencies

        with (
            patch("skilz.installer.detect_agent", return_value="claude"),
            patch("skilz.installer.get_agent_display_name", return_value="Claude Code"),
            patch("skilz.installer.get_agent_default_mode", return_value="copy"),
            patch("skilz.installer.lookup_skill", return_value=deps["skill_info"]),
            patch("skilz.installer.ensure_skills_dir", return_value=deps["skills_dir"]),
            patch("skilz.installer.needs_install", return_value=(True, "not_installed")),
            patch("skilz.installer.clone_or_fetch", return_value=deps["cache_path"]),
            patch("skilz.installer.parse_skill_path", return_value=("main", "skills/test-skill")),
            patch("skilz.installer.checkout_sha"),
            patch("skilz.installer.get_skill_source_path", return_value=deps["source_path"]),
            patch("skilz.installer.ensure_canonical_copy") as mock_canonical,
            patch("skilz.installer.create_symlink"),
            patch("skilz.installer.write_manifest") as mock_write,
        ):
            canonical_path = deps["temp_dir"] / ".skilz" / "skills" / "test-skill"
            canonical_path.mkdir(parents=True)
            mock_canonical.return_value = canonical_path

            # Explicit mode="symlink" should override agent default
            install_skill("test/skill", project_level=True, mode="symlink")

            # Verify ensure_canonical_copy was called
            mock_canonical.assert_called_once()

            # Verify manifest has install_mode="symlink"
            mock_write.assert_called_once()
            manifest = mock_write.call_args[0][1]
            assert manifest.install_mode == "symlink"
            assert manifest.canonical_path is not None

    def test_install_symlink_creates_canonical_copy(self, mock_dependencies):
        """Test that symlink mode creates canonical copy in ~/.skilz/skills/."""
        deps = mock_dependencies

        with (
            patch("skilz.installer.detect_agent", return_value="opencode"),
            patch("skilz.installer.get_agent_display_name", return_value="OpenCode"),
            patch("skilz.installer.get_agent_default_mode", return_value="symlink"),
            patch("skilz.installer.lookup_skill", return_value=deps["skill_info"]),
            patch("skilz.installer.ensure_skills_dir", return_value=deps["skills_dir"]),
            patch("skilz.installer.needs_install", return_value=(True, "not_installed")),
            patch("skilz.installer.clone_or_fetch", return_value=deps["cache_path"]),
            patch("skilz.installer.parse_skill_path", return_value=("main", "skills/test-skill")),
            patch("skilz.installer.checkout_sha"),
            patch("skilz.installer.get_skill_source_path", return_value=deps["source_path"]),
            patch("skilz.installer.ensure_canonical_copy") as mock_canonical,
            patch("skilz.installer.create_symlink") as mock_symlink,
            patch("skilz.installer.write_manifest"),
        ):
            canonical_path = deps["temp_dir"] / ".skilz" / "skills" / "test-skill"
            canonical_path.mkdir(parents=True)
            mock_canonical.return_value = canonical_path

            install_skill("test/skill", project_level=True)

            # Verify ensure_canonical_copy was called with correct args
            mock_canonical.assert_called_once()
            call_kwargs = mock_canonical.call_args[1]
            assert call_kwargs["skill_name"] == "test-skill"
            assert call_kwargs["global_install"] is True

            # Verify create_symlink was called
            mock_symlink.assert_called_once()

    def test_install_verbose_shows_mode(self, mock_dependencies, capsys):
        """Test verbose output includes install mode."""
        deps = mock_dependencies

        with (
            patch("skilz.installer.detect_agent", return_value="claude"),
            patch("skilz.installer.get_agent_display_name", return_value="Claude Code"),
            patch("skilz.installer.get_agent_default_mode", return_value="copy"),
            patch("skilz.installer.lookup_skill", return_value=deps["skill_info"]),
            patch("skilz.installer.ensure_skills_dir", return_value=deps["skills_dir"]),
            patch("skilz.installer.needs_install", return_value=(True, "not_installed")),
            patch("skilz.installer.clone_or_fetch", return_value=deps["cache_path"]),
            patch("skilz.installer.parse_skill_path", return_value=("main", "skills/test-skill")),
            patch("skilz.installer.checkout_sha"),
            patch("skilz.installer.get_skill_source_path", return_value=deps["source_path"]),
            patch("skilz.installer.write_manifest"),
        ):
            install_skill("test/skill", project_level=True, verbose=True)

        captured = capsys.readouterr()
        assert "Install mode: copy" in captured.out
        assert "agent default" in captured.out

    def test_install_manifest_includes_install_mode(self, mock_dependencies):
        """Test that manifest includes install_mode field."""
        deps = mock_dependencies

        with (
            patch("skilz.installer.detect_agent", return_value="claude"),
            patch("skilz.installer.get_agent_display_name", return_value="Claude Code"),
            patch("skilz.installer.get_agent_default_mode", return_value="copy"),
            patch("skilz.installer.lookup_skill", return_value=deps["skill_info"]),
            patch("skilz.installer.ensure_skills_dir", return_value=deps["skills_dir"]),
            patch("skilz.installer.needs_install", return_value=(True, "not_installed")),
            patch("skilz.installer.clone_or_fetch", return_value=deps["cache_path"]),
            patch("skilz.installer.parse_skill_path", return_value=("main", "skills/test-skill")),
            patch("skilz.installer.checkout_sha"),
            patch("skilz.installer.get_skill_source_path", return_value=deps["source_path"]),
            patch("skilz.installer.write_manifest") as mock_write,
        ):
            install_skill("test/skill", project_level=True, mode="copy")

            mock_write.assert_called_once()
            manifest = mock_write.call_args[0][1]
            assert hasattr(manifest, "install_mode")
            assert manifest.install_mode == "copy"


class TestConfigSyncSkip:
    """Tests for SKILZ-49: Skip config sync for native agents."""

    @pytest.fixture
    def mock_skill_info(self):
        """Create a mock SkillInfo for testing."""
        return SkillInfo(
            skill_id="test/skill",
            git_repo="https://github.com/test/repo.git",
            skill_path="/main/skills/test-skill",
            git_sha="abc123def456789012345678901234567890abcd",
        )

    @pytest.fixture
    def mock_dependencies(self, temp_dir, mock_skill_info):
        """Set up common mocks for install_skill."""
        cache_path = temp_dir / "cache" / "repo"
        cache_path.mkdir(parents=True)

        source_path = cache_path / "skills" / "test-skill"
        source_path.mkdir(parents=True)
        (source_path / "SKILL.md").write_text("# Test Skill")

        skills_dir = temp_dir / ".claude" / "skills"
        skills_dir.mkdir(parents=True)

        return {
            "cache_path": cache_path,
            "source_path": source_path,
            "skills_dir": skills_dir,
            "skill_info": mock_skill_info,
            "temp_dir": temp_dir,
        }

    def test_skip_config_sync_for_claude(self, mock_dependencies, capsys):
        """Config sync should be skipped for Claude (native_skill_support='all')."""
        deps = mock_dependencies

        with (
            patch("skilz.installer.detect_agent", return_value="claude"),
            patch("skilz.installer.get_agent_display_name", return_value="Claude Code"),
            patch("skilz.installer.get_agent_default_mode", return_value="copy"),
            patch("skilz.installer.lookup_skill", return_value=deps["skill_info"]),
            patch("skilz.installer.ensure_skills_dir", return_value=deps["skills_dir"]),
            patch("skilz.installer.needs_install", return_value=(True, "not_installed")),
            patch("skilz.installer.clone_or_fetch", return_value=deps["cache_path"]),
            patch("skilz.installer.parse_skill_path", return_value=("main", "skills/test-skill")),
            patch("skilz.installer.checkout_sha"),
            patch("skilz.installer.get_skill_source_path", return_value=deps["source_path"]),
            patch("skilz.installer.write_manifest"),
            patch("skilz.installer.sync_skill_to_configs") as mock_sync,
        ):
            install_skill("test/skill", project_level=True, verbose=True)

            # Sync should NOT be called for Claude (native support)
            mock_sync.assert_not_called()

        captured = capsys.readouterr()
        assert "Skipping config sync" in captured.out

    def test_force_config_overrides_native_support(self, mock_dependencies, capsys):
        """--force-config should trigger sync even for native agents."""
        deps = mock_dependencies

        with (
            patch("skilz.installer.detect_agent", return_value="claude"),
            patch("skilz.installer.get_agent_display_name", return_value="Claude Code"),
            patch("skilz.installer.get_agent_default_mode", return_value="copy"),
            patch("skilz.installer.lookup_skill", return_value=deps["skill_info"]),
            patch("skilz.installer.ensure_skills_dir", return_value=deps["skills_dir"]),
            patch("skilz.installer.needs_install", return_value=(True, "not_installed")),
            patch("skilz.installer.clone_or_fetch", return_value=deps["cache_path"]),
            patch("skilz.installer.parse_skill_path", return_value=("main", "skills/test-skill")),
            patch("skilz.installer.checkout_sha"),
            patch("skilz.installer.get_skill_source_path", return_value=deps["source_path"]),
            patch("skilz.installer.write_manifest"),
            patch("skilz.installer.sync_skill_to_configs") as mock_sync,
        ):
            mock_sync.return_value = []

            install_skill("test/skill", project_level=True, force_config=True)

            # Sync SHOULD be called with --force-config
            mock_sync.assert_called_once()

    def test_config_sync_for_gemini(self, mock_dependencies, capsys):
        """Config sync should be skipped for Gemini (native_skill_support='all', SKILZ-49)."""
        deps = mock_dependencies

        with (
            patch("skilz.installer.detect_agent", return_value="gemini"),
            patch("skilz.installer.get_agent_display_name", return_value="Gemini CLI"),
            patch("skilz.installer.get_agent_default_mode", return_value="copy"),
            patch("skilz.installer.supports_home_install", return_value=True),
            patch("skilz.installer.lookup_skill", return_value=deps["skill_info"]),
            patch("skilz.installer.ensure_skills_dir", return_value=deps["skills_dir"]),
            patch("skilz.installer.needs_install", return_value=(True, "not_installed")),
            patch("skilz.installer.clone_or_fetch", return_value=deps["cache_path"]),
            patch("skilz.installer.parse_skill_path", return_value=("main", "skills/test-skill")),
            patch("skilz.installer.checkout_sha"),
            patch("skilz.installer.get_skill_source_path", return_value=deps["source_path"]),
            patch("skilz.installer.write_manifest"),
            patch("skilz.installer.sync_skill_to_configs") as mock_sync,
        ):
            mock_sync.return_value = []

            install_skill("test/skill", agent="gemini", project_level=True)

            # Sync should NOT be called for Gemini (now has native support)
            mock_sync.assert_not_called()

    def test_skip_config_sync_for_copilot(self, mock_dependencies, capsys):
        """Config sync should be skipped for Copilot (native_skill_support='all', SKILZ-54)."""
        deps = mock_dependencies

        with (
            patch("skilz.installer.detect_agent", return_value="copilot"),
            patch("skilz.installer.get_agent_display_name", return_value="GitHub Copilot"),
            patch("skilz.installer.get_agent_default_mode", return_value="copy"),
            patch("skilz.installer.supports_home_install", return_value=False),
            patch("skilz.installer.lookup_skill", return_value=deps["skill_info"]),
            patch("skilz.installer.ensure_skills_dir", return_value=deps["skills_dir"]),
            patch("skilz.installer.needs_install", return_value=(True, "not_installed")),
            patch("skilz.installer.clone_or_fetch", return_value=deps["cache_path"]),
            patch("skilz.installer.parse_skill_path", return_value=("main", "skills/test-skill")),
            patch("skilz.installer.checkout_sha"),
            patch("skilz.installer.get_skill_source_path", return_value=deps["source_path"]),
            patch("skilz.installer.write_manifest"),
            patch("skilz.installer.sync_skill_to_configs") as mock_sync,
        ):
            install_skill("test/skill", agent="copilot", project_level=True, verbose=True)

            # Sync should NOT be called for Copilot (native support)
            mock_sync.assert_not_called()

        captured = capsys.readouterr()
        assert "Skipping config sync" in captured.out

    def test_local_skill_skip_config_sync_for_claude(self, temp_dir, capsys):
        """Local skill install should skip config sync for Claude."""
        source = temp_dir / "my-skill"
        source.mkdir()
        (source / "SKILL.md").write_text("# My Skill")

        skills_dir = temp_dir / ".claude" / "skills"
        skills_dir.mkdir(parents=True)

        with (
            patch("skilz.installer.detect_agent", return_value="claude"),
            patch("skilz.installer.ensure_skills_dir", return_value=skills_dir),
            patch("skilz.installer.write_manifest"),
            patch("skilz.installer.sync_skill_to_configs") as mock_sync,
        ):
            install_local_skill(source, project_level=True, verbose=True)

            # Sync should NOT be called
            mock_sync.assert_not_called()

        captured = capsys.readouterr()
        assert "Skipping config sync" in captured.out

    def test_local_skill_force_config_overrides(self, temp_dir):
        """Local skill with --force-config should sync for Claude."""
        source = temp_dir / "my-skill"
        source.mkdir()
        (source / "SKILL.md").write_text("# My Skill")

        skills_dir = temp_dir / ".claude" / "skills"
        skills_dir.mkdir(parents=True)

        with (
            patch("skilz.installer.detect_agent", return_value="claude"),
            patch("skilz.installer.ensure_skills_dir", return_value=skills_dir),
            patch("skilz.installer.write_manifest"),
            patch("skilz.installer.sync_skill_to_configs") as mock_sync,
        ):
            mock_sync.return_value = []

            install_local_skill(source, project_level=True, force_config=True)

            # Sync SHOULD be called with --force-config
            mock_sync.assert_called_once()


class TestInstallSkillPathFallback:
    """Tests for skill path fallback with warning (Feature 11)."""

    @pytest.fixture
    def mock_dependencies(self, temp_dir):
        """Common test fixtures for path fallback tests."""
        cache_path = temp_dir / "cache"
        cache_path.mkdir()

        source_path = cache_path / "skills" / "test-skill"
        source_path.mkdir(parents=True)
        (source_path / "SKILL.md").write_text("# Test Skill")

        skills_dir = temp_dir / ".claude" / "skills"
        skills_dir.mkdir(parents=True)

        skill_info = SkillInfo(
            skill_id="test/skill",
            git_repo="https://github.com/test/repo.git",
            skill_path="/main/old-location/SKILL.md",
            git_sha="abc123def456",
        )

        return {
            "cache_path": cache_path,
            "source_path": source_path,
            "skills_dir": skills_dir,
            "skill_info": skill_info,
        }

    def test_install_skill_warns_on_path_change(self, mock_dependencies, capsys):
        """Warning is displayed when skill found at different path."""
        deps = mock_dependencies
        nonexistent = deps["cache_path"] / "nonexistent"
        found_path = deps["cache_path"] / "new-location" / "my-skill"
        found_path.mkdir(parents=True)
        (found_path / "SKILL.md").write_text("# Test")

        with (
            patch("skilz.installer.detect_agent", return_value="claude"),
            patch("skilz.installer.get_agent_display_name", return_value="Claude Code"),
            patch("skilz.installer.lookup_skill", return_value=deps["skill_info"]),
            patch("skilz.installer.ensure_skills_dir", return_value=deps["skills_dir"]),
            patch("skilz.installer.needs_install", return_value=(True, "not_installed")),
            patch("skilz.installer.clone_or_fetch", return_value=deps["cache_path"]),
            patch("skilz.installer.parse_skill_path", return_value=("main", "old-location")),
            patch("skilz.installer.checkout_sha"),
            patch("skilz.installer.get_skill_source_path", return_value=nonexistent),
            patch("skilz.installer.find_skill_by_name", return_value=found_path),
            patch("skilz.installer.write_manifest"),
        ):
            install_skill("test/skill", project_level=True)

        captured = capsys.readouterr()
        # skill_name is derived from skill_path: /main/old-location/SKILL.md -> "old-location"
        assert "Warning: Skill 'old-location' found at different path than expected" in captured.err

    def test_install_skill_no_warning_when_path_matches(self, mock_dependencies, capsys):
        """No warning when skill found at expected path."""
        deps = mock_dependencies

        with (
            patch("skilz.installer.detect_agent", return_value="claude"),
            patch("skilz.installer.get_agent_display_name", return_value="Claude Code"),
            patch("skilz.installer.lookup_skill", return_value=deps["skill_info"]),
            patch("skilz.installer.ensure_skills_dir", return_value=deps["skills_dir"]),
            patch("skilz.installer.needs_install", return_value=(True, "not_installed")),
            patch("skilz.installer.clone_or_fetch", return_value=deps["cache_path"]),
            patch("skilz.installer.parse_skill_path", return_value=("main", "skills/test-skill")),
            patch("skilz.installer.checkout_sha"),
            patch("skilz.installer.get_skill_source_path", return_value=deps["source_path"]),
            patch("skilz.installer.write_manifest"),
        ):
            install_skill("test/skill", project_level=True)

        captured = capsys.readouterr()
        assert "Warning:" not in captured.err
        assert "different path" not in captured.err

    def test_install_skill_warning_goes_to_stderr(self, mock_dependencies, capsys):
        """Warning message goes to stderr, not stdout."""
        deps = mock_dependencies
        nonexistent = deps["cache_path"] / "nonexistent"
        found_path = deps["cache_path"] / "new-location" / "my-skill"
        found_path.mkdir(parents=True)
        (found_path / "SKILL.md").write_text("# Test")

        with (
            patch("skilz.installer.detect_agent", return_value="claude"),
            patch("skilz.installer.get_agent_display_name", return_value="Claude Code"),
            patch("skilz.installer.lookup_skill", return_value=deps["skill_info"]),
            patch("skilz.installer.ensure_skills_dir", return_value=deps["skills_dir"]),
            patch("skilz.installer.needs_install", return_value=(True, "not_installed")),
            patch("skilz.installer.clone_or_fetch", return_value=deps["cache_path"]),
            patch("skilz.installer.parse_skill_path", return_value=("main", "old-location")),
            patch("skilz.installer.checkout_sha"),
            patch("skilz.installer.get_skill_source_path", return_value=nonexistent),
            patch("skilz.installer.find_skill_by_name", return_value=found_path),
            patch("skilz.installer.write_manifest"),
        ):
            install_skill("test/skill", project_level=True)

        captured = capsys.readouterr()
        # Warning should be in stderr, not stdout
        assert "Warning:" in captured.err
        assert "Warning:" not in captured.out
