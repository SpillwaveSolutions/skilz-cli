"""Tests for the registry module."""

import pytest
from pathlib import Path

from skilz.registry import (
    SkillInfo,
    get_registry_paths,
    load_registry,
    lookup_skill,
)
from skilz.errors import RegistryError, SkillNotFoundError


class TestSkillInfo:
    """Tests for SkillInfo dataclass."""

    def test_skill_name_from_path(self):
        """Extract skill name from skill_path."""
        info = SkillInfo(
            skill_id="anthropics/web-artifacts-builder",
            git_repo="https://github.com/anthropics/skills.git",
            skill_path="/main/skills/web-artifacts-builder/SKILL.md",
            git_sha="abc123",
        )
        assert info.skill_name == "web-artifacts-builder"

    def test_skill_name_from_root_skill(self):
        """Fall back to skill_id when SKILL.md is at repo root."""
        info = SkillInfo(
            skill_id="spillwave/plantuml",
            git_repo="https://github.com/SpillwaveSolutions/plantuml.git",
            skill_path="/main/SKILL.md",
            git_sha="abc123",
        )
        # SKILL.md at root → use skill_id
        assert info.skill_name == "plantuml"

    def test_skill_name_fallback_to_id(self):
        """Fall back to skill_id if path is ambiguous."""
        info = SkillInfo(
            skill_id="anthropics/cool-skill",
            git_repo="https://github.com/anthropics/skills.git",
            skill_path="/SKILL.md",
            git_sha="abc123",
        )
        # Should use skill_id since path only has SKILL.md
        assert info.skill_name == "cool-skill"


class TestGetRegistryPaths:
    """Tests for get_registry_paths function."""

    def test_returns_project_and_user_paths(self, temp_dir):
        """Should return both project and user registry paths."""
        paths = get_registry_paths(temp_dir)
        assert len(paths) == 2
        assert paths[0] == temp_dir / ".skilz" / "registry.yaml"
        assert paths[1] == Path.home() / ".skilz" / "registry.yaml"

    def test_project_path_first(self, temp_dir):
        """Project path should have higher priority than user path."""
        paths = get_registry_paths(temp_dir)
        assert "home" not in str(paths[0]).lower() or str(temp_dir) in str(paths[0])


class TestLoadRegistry:
    """Tests for load_registry function."""

    def test_load_valid_registry(self, temp_dir, sample_registry_content):
        """Load a valid registry file."""
        registry_file = temp_dir / "registry.yaml"
        registry_file.write_text(sample_registry_content)

        registry = load_registry(registry_file)

        assert "test/sample-skill" in registry
        assert registry["test/sample-skill"]["git_repo"] == "https://github.com/test/skills.git"

    def test_load_missing_file(self, temp_dir):
        """Raise error for missing file."""
        with pytest.raises(RegistryError) as exc_info:
            load_registry(temp_dir / "nonexistent.yaml")
        assert "File not found" in str(exc_info.value)

    def test_load_invalid_yaml(self, temp_dir):
        """Raise error for invalid YAML."""
        registry_file = temp_dir / "bad.yaml"
        registry_file.write_text("invalid: yaml: content: [")

        with pytest.raises(RegistryError) as exc_info:
            load_registry(registry_file)
        assert "Invalid YAML" in str(exc_info.value)

    def test_load_non_dict_yaml(self, temp_dir):
        """Raise error if YAML is not a dictionary."""
        registry_file = temp_dir / "list.yaml"
        registry_file.write_text("- item1\n- item2")

        with pytest.raises(RegistryError) as exc_info:
            load_registry(registry_file)
        assert "must be a YAML dictionary" in str(exc_info.value)

    def test_load_empty_file(self, temp_dir):
        """Empty file returns empty dict."""
        registry_file = temp_dir / "empty.yaml"
        registry_file.write_text("")

        registry = load_registry(registry_file)
        assert registry == {}


class TestLookupSkill:
    """Tests for lookup_skill function."""

    def test_lookup_existing_skill(self, project_registry):
        """Find a skill in the project registry."""
        skill = lookup_skill("test/sample-skill", project_dir=project_registry)

        assert skill.skill_id == "test/sample-skill"
        assert skill.git_repo == "https://github.com/test/skills.git"
        assert skill.skill_path == "/main/skills/sample-skill"
        assert skill.git_sha == "abc123def456789012345678901234567890abcd"

    def test_lookup_missing_skill(self, project_registry):
        """Raise error for missing skill."""
        with pytest.raises(SkillNotFoundError) as exc_info:
            lookup_skill("nonexistent/skill", project_dir=project_registry)

        assert "nonexistent/skill" in str(exc_info.value)
        assert exc_info.value.skill_id == "nonexistent/skill"

    def test_lookup_no_registries(self, temp_dir):
        """Raise error when no registries exist."""
        # temp_dir has no .skilz directory
        with pytest.raises(SkillNotFoundError):
            lookup_skill("any/skill", project_dir=temp_dir)

    def test_lookup_missing_fields(self, temp_dir):
        """Raise error for skill with missing required fields."""
        registry_dir = temp_dir / ".skilz"
        registry_dir.mkdir()
        registry_file = registry_dir / "registry.yaml"
        registry_file.write_text("""
incomplete/skill:
  git_repo: https://example.com/repo.git
  # missing skill_path and git_sha
""")

        with pytest.raises(RegistryError) as exc_info:
            lookup_skill("incomplete/skill", project_dir=temp_dir)
        assert "missing required fields" in str(exc_info.value)
