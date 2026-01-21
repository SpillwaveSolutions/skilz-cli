"""Tests for config_sync module."""

from pathlib import Path

import pytest

from skilz.agent_registry import AgentConfig
from skilz.config_sync import (
    SECTION_END,
    SECTION_START,
    SkillReference,
    _build_skills_section,
    _generate_usage_template,
    _parse_existing_skills,
    detect_project_config_files,
    format_skill_element,
    sync_skill_to_configs,
    update_config_file,
)


@pytest.fixture
def project_dir(tmp_path: Path) -> Path:
    """Create a temporary project directory."""
    return tmp_path


@pytest.fixture
def skill_ref(project_dir: Path) -> SkillReference:
    """Create a sample skill reference."""
    skill_path = project_dir / ".skilz" / "skills" / "test-skill"
    skill_path.mkdir(parents=True, exist_ok=True)
    # Create a SKILL.md with description
    (skill_path / "SKILL.md").write_text(
        "---\nname: test-skill\ndescription: A test skill for testing\n---\n# Test Skill\n"
    )
    return SkillReference(
        skill_id="owner_repo/test-skill",
        skill_name="test-skill",
        skill_path=skill_path,
    )


@pytest.fixture
def claude_agent() -> AgentConfig:
    """Create a Claude agent config."""
    return AgentConfig(
        name="claude",
        display_name="Claude Code",
        home_dir=Path.home() / ".claude" / "skills",
        project_dir=Path(".claude") / "skills",
        config_files=("CLAUDE.md",),
        supports_home=True,
        default_mode="copy",
        native_skill_support="all",
    )


@pytest.fixture
def gemini_agent() -> AgentConfig:
    """Create a Gemini agent config with native support (current production config)."""
    return AgentConfig(
        name="gemini",
        display_name="Gemini CLI",
        home_dir=Path.home() / ".gemini" / "skills",
        project_dir=Path(".gemini") / "skills",
        config_files=("GEMINI.md",),
        supports_home=True,
        default_mode="copy",
        native_skill_support="all",
    )


@pytest.fixture
def gemini_agent_no_native() -> AgentConfig:
    """Create a Gemini agent config without native support (for testing force_extended)."""
    return AgentConfig(
        name="gemini",
        display_name="Gemini CLI",
        home_dir=None,
        project_dir=Path(".skilz") / "skills",
        config_files=("GEMINI.md",),
        supports_home=False,
        default_mode="symlink",
        native_skill_support="none",
    )


class TestSkillReference:
    """Tests for SkillReference dataclass."""

    def test_skill_reference_creation(self, project_dir: Path) -> None:
        """Test creating a skill reference."""
        skill_ref = SkillReference(
            skill_id="owner_repo/my-skill",
            skill_name="my-skill",
            skill_path=project_dir / "skills" / "my-skill",
        )
        assert skill_ref.skill_id == "owner_repo/my-skill"
        assert skill_ref.skill_name == "my-skill"

    def test_skill_reference_with_description(self, project_dir: Path) -> None:
        """Test creating a skill reference with description."""
        skill_ref = SkillReference(
            skill_id="owner_repo/my-skill",
            skill_name="my-skill",
            skill_path=project_dir / "skills" / "my-skill",
            description="A helpful skill",
        )
        assert skill_ref.description == "A helpful skill"


class TestFormatSkillElement:
    """Tests for format_skill_element function."""

    def test_format_skill_element(self, skill_ref: SkillReference, project_dir: Path) -> None:
        """Test formatting a skill as XML element."""
        result = format_skill_element(skill_ref, project_dir)
        assert "<skill>" in result
        assert "<name>test-skill</name>" in result
        assert "<description>" in result
        assert "<location>" in result
        assert "</skill>" in result

    def test_format_uses_relative_path(self, skill_ref: SkillReference, project_dir: Path) -> None:
        """Test that paths are relative to project directory."""
        result = format_skill_element(skill_ref, project_dir)
        # Should NOT contain absolute path
        assert str(project_dir) not in result
        # Should contain relative path
        assert ".skilz/skills/test-skill/SKILL.md" in result

    def test_format_extracts_description_from_skill_md(
        self, skill_ref: SkillReference, project_dir: Path
    ) -> None:
        """Test that description is extracted from SKILL.md."""
        result = format_skill_element(skill_ref, project_dir)
        assert "A test skill for testing" in result


class TestDetectProjectConfigFiles:
    """Tests for detect_project_config_files function."""

    def test_detect_existing_config_files(self, project_dir: Path) -> None:
        """Test detecting existing config files."""
        # Create CLAUDE.md and GEMINI.md
        (project_dir / "CLAUDE.md").write_text("# Claude")
        (project_dir / "GEMINI.md").write_text("# Gemini")

        results = detect_project_config_files(project_dir)

        agent_names = [r[0] for r in results]
        assert "claude" in agent_names
        assert "gemini" in agent_names

    def test_detect_specific_agent(self, project_dir: Path) -> None:
        """Test detecting config files for a specific agent."""
        # Create both files
        (project_dir / "CLAUDE.md").write_text("# Claude")
        (project_dir / "GEMINI.md").write_text("# Gemini")

        # Only request gemini
        results = detect_project_config_files(project_dir, agent="gemini")

        assert len(results) == 1
        assert results[0][0] == "gemini"

    def test_detect_returns_empty_for_no_configs(self, project_dir: Path) -> None:
        """Test that empty list is returned when no config files exist."""
        results = detect_project_config_files(project_dir)
        assert results == []


class TestUpdateConfigFile:
    """Tests for update_config_file function."""

    def test_creates_new_config_file(
        self,
        project_dir: Path,
        skill_ref: SkillReference,
        gemini_agent: AgentConfig,
    ) -> None:
        """Test creating a new config file."""
        config_path = project_dir / "GEMINI.md"

        result = update_config_file(
            config_path=config_path,
            skill=skill_ref,
            agent_config=gemini_agent,
            project_dir=project_dir,
            create_if_missing=True,
        )

        assert result.created is True
        assert result.updated is True
        assert config_path.exists()

        content = config_path.read_text()
        assert SECTION_START in content
        assert SECTION_END in content
        assert "<skills_system" in content
        assert "<available_skills>" in content
        assert "<skill>" in content
        assert "test-skill" in content

    def test_updates_existing_config_file(
        self,
        project_dir: Path,
        skill_ref: SkillReference,
        gemini_agent: AgentConfig,
    ) -> None:
        """Test updating an existing config file."""
        config_path = project_dir / "GEMINI.md"
        config_path.write_text("# GEMINI.md\n\nSome existing content.\n")

        result = update_config_file(
            config_path=config_path,
            skill=skill_ref,
            agent_config=gemini_agent,
            project_dir=project_dir,
        )

        assert result.created is False
        assert result.updated is True

        content = config_path.read_text()
        assert "Some existing content." in content
        assert "<skill>" in content
        assert "test-skill" in content

    def test_idempotent_does_not_duplicate(
        self,
        project_dir: Path,
        skill_ref: SkillReference,
        gemini_agent: AgentConfig,
    ) -> None:
        """Test that running twice doesn't duplicate entries."""
        config_path = project_dir / "GEMINI.md"

        # First update
        update_config_file(
            config_path=config_path,
            skill=skill_ref,
            agent_config=gemini_agent,
            project_dir=project_dir,
            create_if_missing=True,
        )

        # Second update
        result = update_config_file(
            config_path=config_path,
            skill=skill_ref,
            agent_config=gemini_agent,
            project_dir=project_dir,
        )

        assert result.updated is False  # No update needed

        content = config_path.read_text()
        # Count skill entries (lines with <skill>)
        skill_count = content.count("<skill>")
        assert skill_count == 1

    def test_does_not_create_when_flag_false(
        self,
        project_dir: Path,
        skill_ref: SkillReference,
        gemini_agent: AgentConfig,
    ) -> None:
        """Test that file is not created when create_if_missing=False."""
        config_path = project_dir / "GEMINI.md"

        result = update_config_file(
            config_path=config_path,
            skill=skill_ref,
            agent_config=gemini_agent,
            project_dir=project_dir,
            create_if_missing=False,
        )

        assert result.error == "Config file does not exist"
        assert not config_path.exists()


class TestParseExistingSkills:
    """Tests for _parse_existing_skills function."""

    def test_parse_skills_from_section(self) -> None:
        """Test parsing skill tuples from managed section."""
        content = f"""
# Config

<skills_system priority="1">

## Available Skills

{SECTION_START}
<usage>...</usage>

<available_skills>

<skill>
<name>skill-one</name>
<description>First skill</description>
<location>.skilz/skills/skill-one/SKILL.md</location>
</skill>

<skill>
<name>skill-two</name>
<description>Second skill</description>
<location>.skilz/skills/skill-two/SKILL.md</location>
</skill>

</available_skills>
{SECTION_END}

</skills_system>
"""
        skills = _parse_existing_skills(content)
        assert len(skills) == 2
        assert ("skill-one", "First skill", ".skilz/skills/skill-one/SKILL.md") in skills
        assert ("skill-two", "Second skill", ".skilz/skills/skill-two/SKILL.md") in skills

    def test_parse_empty_when_no_section(self) -> None:
        """Test that empty list is returned when no managed section."""
        content = "# Just a config file\n"
        skills = _parse_existing_skills(content)
        assert skills == []


class TestSyncSkillToConfigs:
    """Tests for sync_skill_to_configs function."""

    def test_sync_to_all_existing_configs(
        self, project_dir: Path, skill_ref: SkillReference
    ) -> None:
        """Test syncing to all existing config files."""
        (project_dir / "CLAUDE.md").write_text("# Claude")
        (project_dir / "GEMINI.md").write_text("# Gemini")

        results = sync_skill_to_configs(
            skill=skill_ref,
            project_dir=project_dir,
        )

        assert len(results) == 2
        updated_agents = {r.agent_name for r in results if r.updated}
        assert "claude" in updated_agents
        assert "gemini" in updated_agents

    def test_sync_to_specific_agent_creates_file(
        self, project_dir: Path, skill_ref: SkillReference
    ) -> None:
        """Test syncing to specific agent creates config file if needed."""
        results = sync_skill_to_configs(
            skill=skill_ref,
            project_dir=project_dir,
            agent="gemini",
        )

        assert len(results) == 1
        assert results[0].agent_name == "gemini"
        assert results[0].created is True
        assert (project_dir / "GEMINI.md").exists()

    def test_sync_skips_nonexistent_when_no_agent(
        self, project_dir: Path, skill_ref: SkillReference
    ) -> None:
        """Test that non-existent configs are skipped when agent not specified."""
        # No config files exist
        results = sync_skill_to_configs(
            skill=skill_ref,
            project_dir=project_dir,
        )

        assert len(results) == 0


class TestAgentSkillsIOFormat:
    """Tests to verify agentskills.io standard compliance."""

    def test_output_follows_standard_format(
        self,
        project_dir: Path,
        skill_ref: SkillReference,
        gemini_agent: AgentConfig,
    ) -> None:
        """Test that output follows the agentskills.io standard format."""
        config_path = project_dir / "GEMINI.md"

        update_config_file(
            config_path=config_path,
            skill=skill_ref,
            agent_config=gemini_agent,
            project_dir=project_dir,
            create_if_missing=True,
        )

        content = config_path.read_text()

        # Check for required structure elements
        assert "<skills_system priority=" in content
        assert "<usage>" in content
        assert "</usage>" in content
        assert "<available_skills>" in content
        assert "</available_skills>" in content
        assert "<!-- SKILLS_TABLE_START -->" in content
        assert "<!-- SKILLS_TABLE_END -->" in content

        # Check skill element structure
        assert "<skill>" in content
        assert "<name>" in content
        assert "</name>" in content
        assert "<description>" in content
        assert "</description>" in content
        assert "<location>" in content
        assert "</location>" in content
        assert "</skill>" in content


class TestGenerateUsageTemplate:
    """Tests for _generate_usage_template function."""

    def test_claude_native_all_no_agent_flag(self) -> None:
        """Claude with native_skill_support='all' should not have --agent flag."""
        result = _generate_usage_template("claude", "all")
        assert 'skilz read <skill-name>"' in result
        assert "--agent" not in result

    def test_codex_native_all_has_agent_flag(self) -> None:
        """Codex with native_skill_support='all' should have --agent codex."""
        result = _generate_usage_template("codex", "all")
        assert "--agent codex" in result

    def test_gemini_native_none_has_agent_flag(self) -> None:
        """Gemini with native_skill_support='none' should have --agent gemini."""
        result = _generate_usage_template("gemini", "none")
        assert "--agent gemini" in result

    def test_gemini_native_none_has_extended_instructions(self) -> None:
        """Agents with native_skill_support='none' should have step-by-step process."""
        result = _generate_usage_template("gemini", "none")
        assert "Step-by-step process:" in result
        assert "1. Identify a skill" in result

    def test_opencode_native_home_has_agent_flag(self) -> None:
        """OpenCode with native_skill_support='home' should have --agent opencode."""
        result = _generate_usage_template("opencode", "home")
        assert "--agent opencode" in result

    def test_opencode_native_home_no_extended_instructions(self) -> None:
        """Agents with native_skill_support='home' should NOT have extended instructions."""
        result = _generate_usage_template("opencode", "home")
        assert "Step-by-step process:" not in result

    def test_qwen_native_none_has_extended_instructions(self) -> None:
        """QWEN with native_skill_support='none' should have extended instructions."""
        result = _generate_usage_template("qwen", "none")
        assert "--agent qwen" in result
        assert "Step-by-step process:" in result


class TestBuildSkillsSectionWithAgent:
    """Tests for _build_skills_section with agent parameters."""

    def test_build_section_claude_no_agent_flag(self, tmp_path: Path) -> None:
        """Building section for Claude should not include --agent flag."""
        skill = SkillReference(
            skill_id="test/skill",
            skill_name="test-skill",
            skill_path=tmp_path / "test-skill",
            description="Test skill",
        )
        (tmp_path / "test-skill").mkdir()
        (tmp_path / "test-skill" / "SKILL.md").write_text("# Test")

        result = _build_skills_section(
            [skill],
            project_dir=tmp_path,
            agent_name="claude",
            native_support="all",
        )
        assert 'skilz read <skill-name>"' in result
        assert "--agent" not in result

    def test_build_section_gemini_has_agent_flag(self, tmp_path: Path) -> None:
        """Building section for Gemini should include --agent gemini."""
        skill = SkillReference(
            skill_id="test/skill",
            skill_name="test-skill",
            skill_path=tmp_path / "test-skill",
            description="Test skill",
        )
        (tmp_path / "test-skill").mkdir()
        (tmp_path / "test-skill" / "SKILL.md").write_text("# Test")

        result = _build_skills_section(
            [skill],
            project_dir=tmp_path,
            agent_name="gemini",
            native_support="none",
        )
        assert "--agent gemini" in result
        assert "Step-by-step process:" in result


class TestUpdateConfigFileAgentSpecific:
    """Tests for agent-specific behavior in update_config_file."""

    def test_claude_config_no_agent_flag(
        self,
        project_dir: Path,
        skill_ref: SkillReference,
        claude_agent: AgentConfig,
    ) -> None:
        """Test that Claude config file doesn't include --agent flag."""
        config_path = project_dir / "CLAUDE.md"

        update_config_file(
            config_path=config_path,
            skill=skill_ref,
            agent_config=claude_agent,
            project_dir=project_dir,
            create_if_missing=True,
        )

        content = config_path.read_text()
        assert 'skilz read <skill-name>"' in content
        assert "--agent" not in content

    def test_gemini_native_config_no_extended_instructions(
        self,
        project_dir: Path,
        skill_ref: SkillReference,
        gemini_agent: AgentConfig,
    ) -> None:
        """Test that Gemini with native support doesn't get extended instructions."""
        config_path = project_dir / "GEMINI.md"

        update_config_file(
            config_path=config_path,
            skill=skill_ref,
            agent_config=gemini_agent,
            project_dir=project_dir,
            create_if_missing=True,
        )

        content = config_path.read_text()
        assert "--agent gemini" in content
        # Native support means NO extended instructions
        assert "Step-by-step process:" not in content

    def test_gemini_no_native_config_has_extended_instructions(
        self,
        project_dir: Path,
        skill_ref: SkillReference,
        gemini_agent_no_native: AgentConfig,
    ) -> None:
        """Test that Gemini without native support gets extended instructions."""
        config_path = project_dir / "GEMINI.md"

        update_config_file(
            config_path=config_path,
            skill=skill_ref,
            agent_config=gemini_agent_no_native,
            project_dir=project_dir,
            create_if_missing=True,
        )

        content = config_path.read_text()
        assert "--agent gemini" in content
        assert "Step-by-step process:" in content


class TestForceExtendedInstructions:
    """Tests for force_extended parameter (--force-config behavior)."""

    def test_force_extended_adds_instructions_for_native_agent(
        self,
        project_dir: Path,
        skill_ref: SkillReference,
        gemini_agent: AgentConfig,
    ) -> None:
        """Test that force_extended adds step-by-step instructions even for native agents."""
        config_path = project_dir / "GEMINI.md"

        # Gemini has native_skill_support="all", but force_extended should add instructions
        update_config_file(
            config_path=config_path,
            skill=skill_ref,
            agent_config=gemini_agent,
            project_dir=project_dir,
            create_if_missing=True,
            force_extended=True,
        )

        content = config_path.read_text()
        assert "--agent gemini" in content
        # force_extended=True should add extended instructions
        assert "Step-by-step process:" in content

    def test_generate_usage_template_force_extended(self) -> None:
        """Test _generate_usage_template with force_extended=True."""
        # Gemini with native support normally wouldn't get extended instructions
        result = _generate_usage_template("gemini", "all", force_extended=False)
        assert "Step-by-step process:" not in result

        # But with force_extended=True, it should
        result = _generate_usage_template("gemini", "all", force_extended=True)
        assert "Step-by-step process:" in result
        assert "--agent gemini" in result

    def test_claude_force_extended_still_no_agent_flag(self) -> None:
        """Test that Claude still doesn't get --agent flag even with force_extended."""
        result = _generate_usage_template("claude", "all", force_extended=True)
        # Claude should never have --agent flag
        assert "--agent" not in result
        # But should have extended instructions when forced
        assert "Step-by-step process:" in result
