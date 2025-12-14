"""Tests for the manifest module."""

import pytest
from pathlib import Path

from skilz.manifest import (
    SkillManifest,
    write_manifest,
    read_manifest,
    needs_install,
    MANIFEST_FILENAME,
)


class TestSkillManifest:
    """Tests for SkillManifest dataclass."""

    def test_create_manifest(self):
        """Create a manifest with current timestamp."""
        manifest = SkillManifest.create(
            skill_id="test/skill",
            git_repo="https://github.com/test/repo.git",
            skill_path="/main/skills/test-skill",
            git_sha="abc123def456789012345678901234567890abcd",
        )

        assert manifest.skill_id == "test/skill"
        assert manifest.git_repo == "https://github.com/test/repo.git"
        assert manifest.skill_path == "/main/skills/test-skill"
        assert manifest.git_sha == "abc123def456789012345678901234567890abcd"
        assert manifest.skilz_version == "0.1.0"
        assert "T" in manifest.installed_at  # ISO format has T separator

    def test_to_dict(self):
        """Convert manifest to dictionary."""
        manifest = SkillManifest.create(
            skill_id="test/skill",
            git_repo="https://github.com/test/repo.git",
            skill_path="/main/skills/test-skill",
            git_sha="abc123",
        )

        data = manifest.to_dict()

        assert data["skill_id"] == "test/skill"
        assert data["git_repo"] == "https://github.com/test/repo.git"
        assert "installed_at" in data


class TestWriteManifest:
    """Tests for write_manifest function."""

    def test_write_manifest_creates_file(self, temp_dir):
        """Write manifest creates file."""
        skill_dir = temp_dir / "my-skill"
        skill_dir.mkdir()

        manifest = SkillManifest.create(
            skill_id="test/skill",
            git_repo="https://github.com/test/repo.git",
            skill_path="/main/skills/test-skill",
            git_sha="abc123",
        )

        result = write_manifest(skill_dir, manifest)

        assert result.exists()
        assert result.name == MANIFEST_FILENAME
        assert "skill_id: test/skill" in result.read_text()


class TestReadManifest:
    """Tests for read_manifest function."""

    def test_read_valid_manifest(self, temp_dir):
        """Read a valid manifest file."""
        skill_dir = temp_dir / "my-skill"
        skill_dir.mkdir()

        # Write a manifest first
        manifest = SkillManifest.create(
            skill_id="test/skill",
            git_repo="https://github.com/test/repo.git",
            skill_path="/main/skills/test-skill",
            git_sha="abc123def456789012345678901234567890abcd",
        )
        write_manifest(skill_dir, manifest)

        # Read it back
        result = read_manifest(skill_dir)

        assert result is not None
        assert result.skill_id == "test/skill"
        assert result.git_sha == "abc123def456789012345678901234567890abcd"

    def test_read_missing_manifest(self, temp_dir):
        """Return None for missing manifest."""
        skill_dir = temp_dir / "my-skill"
        skill_dir.mkdir()

        result = read_manifest(skill_dir)

        assert result is None

    def test_read_invalid_manifest(self, temp_dir):
        """Return None for invalid manifest."""
        skill_dir = temp_dir / "my-skill"
        skill_dir.mkdir()
        (skill_dir / MANIFEST_FILENAME).write_text("not: valid: yaml: [")

        result = read_manifest(skill_dir)

        assert result is None

    def test_read_incomplete_manifest(self, temp_dir):
        """Return None for manifest missing required fields."""
        skill_dir = temp_dir / "my-skill"
        skill_dir.mkdir()
        (skill_dir / MANIFEST_FILENAME).write_text("skill_id: test\n")

        result = read_manifest(skill_dir)

        assert result is None


class TestNeedsInstall:
    """Tests for needs_install function."""

    def test_needs_install_if_not_exists(self, temp_dir):
        """Needs install if directory doesn't exist."""
        skill_dir = temp_dir / "nonexistent"

        needs, reason = needs_install(skill_dir, "abc123")

        assert needs is True
        assert reason == "not_installed"

    def test_needs_install_if_no_manifest(self, temp_dir):
        """Needs install if directory exists but no manifest."""
        skill_dir = temp_dir / "my-skill"
        skill_dir.mkdir()

        needs, reason = needs_install(skill_dir, "abc123")

        assert needs is True
        assert reason == "no_manifest"

    def test_needs_install_if_sha_differs(self, temp_dir):
        """Needs install if SHA differs."""
        skill_dir = temp_dir / "my-skill"
        skill_dir.mkdir()

        # Write manifest with different SHA
        manifest = SkillManifest.create(
            skill_id="test/skill",
            git_repo="https://github.com/test/repo.git",
            skill_path="/main/skills/test-skill",
            git_sha="old_sha_value",
        )
        write_manifest(skill_dir, manifest)

        needs, reason = needs_install(skill_dir, "new_sha_value")

        assert needs is True
        assert reason == "sha_mismatch"

    def test_up_to_date_if_sha_matches(self, temp_dir):
        """No install needed if SHA matches."""
        skill_dir = temp_dir / "my-skill"
        skill_dir.mkdir()

        # Write manifest with same SHA
        manifest = SkillManifest.create(
            skill_id="test/skill",
            git_repo="https://github.com/test/repo.git",
            skill_path="/main/skills/test-skill",
            git_sha="matching_sha",
        )
        write_manifest(skill_dir, manifest)

        needs, reason = needs_install(skill_dir, "matching_sha")

        assert needs is False
        assert reason == "up_to_date"
