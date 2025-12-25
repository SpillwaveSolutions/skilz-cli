"""Tests for the scanner module."""

import pytest

from skilz.manifest import SkillManifest, write_manifest
from skilz.scanner import (
    _create_broken_skill_placeholder,
    find_installed_skill,
    scan_installed_skills,
    scan_skills_directory,
)


@pytest.fixture
def skills_dir_with_skills(temp_dir):
    """Create a skills directory with some installed skills."""
    skills_dir = temp_dir / ".claude" / "skills"
    skills_dir.mkdir(parents=True)

    # Create first skill
    skill1_dir = skills_dir / "plantuml"
    skill1_dir.mkdir()
    (skill1_dir / "SKILL.md").write_text("# Plantuml Skill")
    manifest1 = SkillManifest.create(
        skill_id="spillwave/plantuml",
        git_repo="https://github.com/SpillwaveSolutions/plantuml.git",
        skill_path="/main/SKILL.md",
        git_sha="f2489dcd47799e4aaff3ae0a34cde0ebf2288a66",
    )
    write_manifest(skill1_dir, manifest1)

    # Create second skill
    skill2_dir = skills_dir / "design-doc-mermaid"
    skill2_dir.mkdir()
    (skill2_dir / "SKILL.md").write_text("# Mermaid Skill")
    manifest2 = SkillManifest.create(
        skill_id="spillwave/design-doc-mermaid",
        git_repo="https://github.com/SpillwaveSolutions/design-doc-mermaid.git",
        skill_path="/v1.0.0/SKILL.md",
        git_sha="e1c29a38abcd1234567890abcdef1234567890ab",
    )
    write_manifest(skill2_dir, manifest2)

    return skills_dir


@pytest.fixture
def skills_dir_empty(temp_dir):
    """Create an empty skills directory."""
    skills_dir = temp_dir / ".claude" / "skills"
    skills_dir.mkdir(parents=True)
    return skills_dir


@pytest.fixture
def skills_dir_no_manifest(temp_dir):
    """Create a skills directory with a skill that has no manifest."""
    skills_dir = temp_dir / ".claude" / "skills"
    skills_dir.mkdir(parents=True)

    # Create skill without manifest
    skill_dir = skills_dir / "no-manifest-skill"
    skill_dir.mkdir()
    (skill_dir / "SKILL.md").write_text("# No Manifest Skill")

    return skills_dir


class TestInstalledSkill:
    """Tests for InstalledSkill dataclass."""

    def test_git_sha_short(self, skills_dir_with_skills):
        """Test short SHA property."""
        skills = scan_skills_directory(skills_dir_with_skills, "claude", False)
        skill = next(s for s in skills if s.skill_name == "plantuml")

        assert skill.git_sha_short == "f2489dcd"
        assert len(skill.git_sha_short) == 8

    def test_installed_at_short(self, skills_dir_with_skills):
        """Test short date property."""
        skills = scan_skills_directory(skills_dir_with_skills, "claude", False)
        skill = skills[0]

        # Should be YYYY-MM-DD format
        assert len(skill.installed_at_short) == 10
        assert skill.installed_at_short.count("-") == 2


class TestScanSkillsDirectory:
    """Tests for scan_skills_directory function."""

    def test_scan_directory_with_skills(self, skills_dir_with_skills):
        """Test scanning a directory with installed skills."""
        skills = scan_skills_directory(skills_dir_with_skills, "claude", False)

        assert len(skills) == 2

        skill_names = {s.skill_name for s in skills}
        assert skill_names == {"plantuml", "design-doc-mermaid"}

    def test_scan_empty_directory(self, skills_dir_empty):
        """Test scanning an empty skills directory."""
        skills = scan_skills_directory(skills_dir_empty, "claude", False)

        assert len(skills) == 0

    def test_scan_nonexistent_directory(self, temp_dir):
        """Test scanning a directory that doesn't exist."""
        nonexistent = temp_dir / "does-not-exist"
        skills = scan_skills_directory(nonexistent, "claude", False)

        assert len(skills) == 0

    def test_scan_skips_skills_without_manifest(self, skills_dir_no_manifest):
        """Test that skills without manifests are skipped."""
        skills = scan_skills_directory(skills_dir_no_manifest, "claude", False)

        assert len(skills) == 0

    def test_scan_extracts_correct_metadata(self, skills_dir_with_skills):
        """Test that skill metadata is correctly extracted."""
        skills = scan_skills_directory(skills_dir_with_skills, "claude", False)
        plantuml = next(s for s in skills if s.skill_name == "plantuml")

        assert plantuml.skill_id == "spillwave/plantuml"
        assert plantuml.skill_name == "plantuml"
        assert plantuml.manifest.git_sha == "f2489dcd47799e4aaff3ae0a34cde0ebf2288a66"
        assert plantuml.agent == "claude"
        assert plantuml.project_level is False


class TestScanInstalledSkills:
    """Tests for scan_installed_skills function."""

    def test_scan_project_level(self, temp_dir, skills_dir_with_skills):
        """Test scanning project-level installations."""
        # skills_dir_with_skills creates .claude/skills in temp_dir
        project_dir = skills_dir_with_skills.parent.parent

        skills = scan_installed_skills(
            agent="claude",
            project_level=True,
            project_dir=project_dir,
        )

        assert len(skills) == 2
        assert all(s.project_level is True for s in skills)

    def test_scan_specific_agent(self, temp_dir, skills_dir_with_skills):
        """Test scanning only a specific agent."""
        project_dir = skills_dir_with_skills.parent.parent

        skills = scan_installed_skills(
            agent="claude",
            project_level=True,
            project_dir=project_dir,
        )

        assert all(s.agent == "claude" for s in skills)

    def test_skills_sorted_by_id(self, skills_dir_with_skills):
        """Test that skills are sorted by skill_id."""
        project_dir = skills_dir_with_skills.parent.parent

        skills = scan_installed_skills(
            agent="claude",
            project_level=True,
            project_dir=project_dir,
        )

        skill_ids = [s.skill_id for s in skills]
        assert skill_ids == sorted(skill_ids)


class TestFindInstalledSkill:
    """Tests for find_installed_skill function."""

    def test_find_by_skill_id(self, skills_dir_with_skills):
        """Test finding a skill by full ID."""
        project_dir = skills_dir_with_skills.parent.parent

        skill = find_installed_skill(
            "spillwave/plantuml",
            agent="claude",
            project_level=True,
            project_dir=project_dir,
        )

        assert skill is not None
        assert skill.skill_id == "spillwave/plantuml"

    def test_find_by_skill_name(self, skills_dir_with_skills):
        """Test finding a skill by name only."""
        project_dir = skills_dir_with_skills.parent.parent

        skill = find_installed_skill(
            "plantuml",
            agent="claude",
            project_level=True,
            project_dir=project_dir,
        )

        assert skill is not None
        assert skill.skill_name == "plantuml"

    def test_find_by_partial_name(self, skills_dir_with_skills):
        """Test finding a skill by partial name (unique match)."""
        project_dir = skills_dir_with_skills.parent.parent

        skill = find_installed_skill(
            "mermaid",
            agent="claude",
            project_level=True,
            project_dir=project_dir,
        )

        assert skill is not None
        assert skill.skill_name == "design-doc-mermaid"

    def test_find_not_found(self, skills_dir_with_skills):
        """Test finding a skill that doesn't exist."""
        project_dir = skills_dir_with_skills.parent.parent

        skill = find_installed_skill(
            "nonexistent-skill",
            agent="claude",
            project_level=True,
            project_dir=project_dir,
        )

        assert skill is None

    def test_find_ambiguous_returns_none(self, skills_dir_with_skills):
        """Test that ambiguous partial matches return None."""
        project_dir = skills_dir_with_skills.parent.parent

        # Both skill names contain "a": plantuml (a), design-doc-mermaid (a)
        skill = find_installed_skill(
            "a",
            agent="claude",
            project_level=True,
            project_dir=project_dir,
        )

        # Should return None for ambiguous matches
        assert skill is None


class TestSymlinkScanning:
    """Tests for symlink detection in scanner."""

    def test_scan_detects_symlinked_skill(self, temp_dir):
        """Test that symlinked skills are detected with correct install_mode."""
        # Create canonical location
        canonical_dir = temp_dir / ".skilz" / "skills" / "pdf"
        canonical_dir.mkdir(parents=True)
        (canonical_dir / "SKILL.md").write_text("# PDF Skill")
        manifest = SkillManifest.create(
            skill_id="anthropics/pdf",
            git_repo="https://github.com/anthropics/pdf.git",
            skill_path="/main/SKILL.md",
            git_sha="abc123def456",
            install_mode="symlink",
            canonical_path=str(canonical_dir),
        )
        write_manifest(canonical_dir, manifest)

        # Create symlink in agent directory
        agent_skills = temp_dir / ".claude" / "skills"
        agent_skills.mkdir(parents=True)
        symlink_path = agent_skills / "pdf"
        symlink_path.symlink_to(canonical_dir)

        # Scan and verify
        skills = scan_skills_directory(agent_skills, "claude", False)

        assert len(skills) == 1
        skill = skills[0]
        assert skill.skill_name == "pdf"
        assert skill.install_mode == "symlink"
        assert skill.canonical_path is not None
        assert skill.is_broken is False

    def test_scan_detects_copy_skill(self, temp_dir):
        """Test that regular (non-symlink) skills have install_mode='copy'."""
        skills_dir = temp_dir / ".claude" / "skills"
        skill_dir = skills_dir / "pdf"
        skill_dir.mkdir(parents=True)
        (skill_dir / "SKILL.md").write_text("# PDF Skill")
        manifest = SkillManifest.create(
            skill_id="anthropics/pdf",
            git_repo="https://github.com/anthropics/pdf.git",
            skill_path="/main/SKILL.md",
            git_sha="abc123def456",
        )
        write_manifest(skill_dir, manifest)

        skills = scan_skills_directory(skills_dir, "claude", False)

        assert len(skills) == 1
        skill = skills[0]
        assert skill.install_mode == "copy"
        assert skill.canonical_path is None
        assert skill.is_broken is False

    def test_scan_detects_broken_symlink(self, temp_dir):
        """Test that broken symlinks are detected and reported."""
        # Create canonical that will be deleted
        canonical_dir = temp_dir / ".skilz" / "skills" / "broken-skill"
        canonical_dir.mkdir(parents=True)

        # Create symlink
        agent_skills = temp_dir / ".claude" / "skills"
        agent_skills.mkdir(parents=True)
        symlink_path = agent_skills / "broken-skill"
        symlink_path.symlink_to(canonical_dir)

        # Break the symlink by removing canonical
        canonical_dir.rmdir()

        # Scan and verify
        skills = scan_skills_directory(agent_skills, "claude", False)

        assert len(skills) == 1
        skill = skills[0]
        assert skill.skill_name == "broken-skill"
        assert skill.is_broken is True
        assert skill.install_mode == "symlink"
        assert "unknown" in skill.skill_id

    def test_installed_skill_to_dict(self, temp_dir):
        """Test InstalledSkill.to_dict includes new fields."""
        skills_dir = temp_dir / ".claude" / "skills"
        skill_dir = skills_dir / "test-skill"
        skill_dir.mkdir(parents=True)
        (skill_dir / "SKILL.md").write_text("# Test")
        manifest = SkillManifest.create(
            skill_id="test/skill",
            git_repo="https://github.com/test/skill.git",
            skill_path="/main/SKILL.md",
            git_sha="abc123",
            install_mode="symlink",
            canonical_path="/path/to/canonical",
        )
        write_manifest(skill_dir, manifest)

        skills = scan_skills_directory(skills_dir, "claude", False)
        skill = skills[0]

        data = skill.to_dict()

        assert "install_mode" in data
        assert "canonical_path" in data
        assert "is_broken" in data
        assert data["is_broken"] is False

    def test_create_broken_skill_placeholder(self, temp_dir):
        """Test _create_broken_skill_placeholder creates valid placeholder."""
        skill_dir = temp_dir / "broken-link"
        canonical = temp_dir / "missing-canonical"

        placeholder = _create_broken_skill_placeholder(
            skill_dir=skill_dir,
            canonical_path=canonical,
            agent="claude",
            project_level=False,
        )

        assert placeholder.is_broken is True
        assert placeholder.skill_name == "broken-link"
        assert placeholder.install_mode == "symlink"
        assert placeholder.canonical_path == canonical
        assert "unknown" in placeholder.skill_id
