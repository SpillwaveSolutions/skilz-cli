"""Tests for the agent_registry module."""

import json
from dataclasses import FrozenInstanceError
from pathlib import Path

import pytest

from skilz.agent_registry import (
    AgentConfig,
    AgentRegistry,
    check_skill_directory_name,
    get_agent_choices,
    get_builtin_agents,
    get_registry,
    rename_skill_directory,
    reset_registry,
    validate_skill_name,
)


class TestAgentConfig:
    """Tests for AgentConfig dataclass."""

    def test_frozen_dataclass(self):
        """AgentConfig is immutable (frozen)."""
        config = AgentConfig(
            name="test",
            display_name="Test Agent",
            home_dir=Path.home() / ".test" / "skills",
            project_dir=Path(".test") / "skills",
            config_files=("TEST.md",),
            supports_home=True,
            default_mode="copy",
            native_skill_support="all",
        )

        with pytest.raises(FrozenInstanceError):
            config.name = "other"  # type: ignore

    def test_from_dict_valid(self):
        """Create AgentConfig from valid dictionary."""
        data = {
            "display_name": "Test Agent",
            "home_dir": "~/.test/skills",
            "project_dir": ".test/skills",
            "config_files": ["TEST.md"],
            "supports_home": True,
            "default_mode": "copy",
            "native_skill_support": "all",
        }

        config = AgentConfig.from_dict("test", data)

        assert config.name == "test"
        assert config.display_name == "Test Agent"
        assert config.home_dir == Path.home() / ".test" / "skills"
        assert config.project_dir == Path(".test/skills")
        assert config.config_files == ("TEST.md",)
        assert config.supports_home is True
        assert config.default_mode == "copy"
        assert config.native_skill_support == "all"

    def test_from_dict_missing_required_field(self):
        """Raise ValueError if required field is missing."""
        data = {
            "display_name": "Test Agent",
            # Missing project_dir
            "default_mode": "copy",
        }

        with pytest.raises(ValueError, match="Missing required field 'project_dir'"):
            AgentConfig.from_dict("test", data)

    def test_from_dict_invalid_default_mode(self):
        """Raise ValueError for invalid default_mode."""
        data = {
            "display_name": "Test Agent",
            "project_dir": ".test/skills",
            "default_mode": "invalid",
        }

        with pytest.raises(ValueError, match="Invalid default_mode 'invalid'"):
            AgentConfig.from_dict("test", data)

    def test_from_dict_invalid_native_skill_support(self):
        """Raise ValueError for invalid native_skill_support."""
        data = {
            "display_name": "Test Agent",
            "project_dir": ".test/skills",
            "default_mode": "copy",
            "native_skill_support": "invalid",
        }

        with pytest.raises(ValueError, match="Invalid native_skill_support 'invalid'"):
            AgentConfig.from_dict("test", data)

    def test_from_dict_defaults(self):
        """Use default values for optional fields."""
        data = {
            "display_name": "Test Agent",
            "project_dir": ".test/skills",
            "default_mode": "symlink",
        }

        config = AgentConfig.from_dict("test", data)

        assert config.home_dir is None
        assert config.config_files == ()
        assert config.supports_home is False
        assert config.native_skill_support == "none"
        assert config.uses_folder_rules is False
        assert config.invocation is None


class TestBuiltinAgents:
    """Tests for built-in agent definitions."""

    def test_all_30_plus_agents_present(self):
        """All 30+ built-in agents are defined (updated for Issues #46, #47, #49)."""
        agents = get_builtin_agents()

        # Original agents
        original_agents = [
            "claude",
            "opencode",
            "codex",
            "gemini",
            "copilot",
            "aider",
            "cursor",
            "windsurf",
            "qwen",
            "crush",
            "kimi",
            "plandex",
            "zed",
            "universal",
        ]

        # New agents from Issues #46, #47, #49
        new_agents = [
            "antigravity",  # Issue #47
            "openhands",
            "cline",
            "goose",
            "roo",
            "kilo",
            "trae",
            "droid",  # Issue #49
            "clawdbot",
            "kiro-cli",
            "pi",
            "neovate",
            "zencoder",
            "amp",
            "qoder",
            "command-code",  # Issue #49
        ]

        # Verify all original agents are still present
        for agent in original_agents:
            assert agent in agents, f"Original agent '{agent}' missing"

        # Verify all new agents are present
        for agent in new_agents:
            assert agent in agents, f"New agent '{agent}' missing"

        assert len(agents) >= 30  # Updated for new agents
        # All agents should be present (checked above), f"Missing agent: {agent}"

    def test_claude_config(self):
        """Claude agent has correct configuration."""
        agents = get_builtin_agents()
        claude = agents["claude"]

        assert claude.name == "claude"
        assert claude.display_name == "Claude Code"
        assert claude.home_dir == Path.home() / ".claude" / "skills"
        assert claude.project_dir == Path(".claude") / "skills"
        assert claude.supports_home is True
        assert claude.default_mode == "copy"
        assert claude.native_skill_support == "all"

    def test_opencode_config(self):
        """OpenCode agent has correct configuration."""
        agents = get_builtin_agents()
        opencode = agents["opencode"]

        assert opencode.name == "opencode"
        assert opencode.display_name == "OpenCode CLI"
        assert opencode.home_dir == Path.home() / ".config" / "opencode" / "skill"  # singular
        assert opencode.project_dir == Path(".opencode") / "skill"  # singular
        assert opencode.supports_home is True
        assert opencode.default_mode == "copy"
        assert opencode.native_skill_support == "all"

    def test_gemini_config(self):
        """Gemini agent has correct configuration with native support (SKILZ-49)."""
        agents = get_builtin_agents()
        gemini = agents["gemini"]

        assert gemini.name == "gemini"
        assert gemini.display_name == "Gemini CLI"
        assert gemini.home_dir == Path.home() / ".gemini" / "skills"
        assert gemini.project_dir == Path(".gemini") / "skills"
        assert gemini.supports_home is True  # Now supports user-level
        assert gemini.default_mode == "copy"
        assert gemini.native_skill_support == "all"  # Native support enabled
        assert gemini.invocation == "/skills or activate_skill tool"

    def test_universal_config(self):
        """Universal agent has correct configuration (SKILZ-50)."""
        agents = get_builtin_agents()
        universal = agents["universal"]

        assert universal.name == "universal"
        assert universal.display_name == "Universal (Skilz)"
        assert universal.home_dir == Path.home() / ".skilz" / "skills"
        assert universal.project_dir == Path(".skilz") / "skills"
        assert universal.config_files == ("AGENTS.md",)  # Now has config file
        assert universal.supports_home is True
        assert universal.default_mode == "copy"
        assert universal.native_skill_support == "none"  # Not native

    def test_copilot_native_support(self):
        """Copilot should have native skill support with global support (updated for Issue #49)."""
        agents = get_builtin_agents()
        copilot = agents["copilot"]

        assert copilot.name == "copilot"
        assert copilot.display_name == "GitHub Copilot"
        assert copilot.home_dir == Path.home() / ".copilot" / "skills"  # Added global support
        assert copilot.project_dir == Path(".github") / "skills"  # Native location
        assert copilot.supports_home is True  # Updated for Issue #49
        assert copilot.default_mode == "copy"
        assert copilot.native_skill_support == "all"  # Skip config sync

    def test_cursor_uses_folder_rules(self):
        """Cursor agent has uses_folder_rules enabled."""
        agents = get_builtin_agents()
        cursor = agents["cursor"]

        assert cursor.uses_folder_rules is True

    def test_codex_has_invocation(self):
        """Codex agent has invocation field set."""
        agents = get_builtin_agents()
        codex = agents["codex"]

        assert codex.invocation == "$skill-name or /skills"


class TestAgentRegistry:
    """Tests for AgentRegistry class."""

    def test_registry_loads_builtin_agents(self):
        """Registry loads all built-in agents by default."""
        registry = AgentRegistry()

        agents = registry.list_agents()
        assert len(agents) >= 30  # Updated for new agents (Issues #46, #47, #49)
        assert "claude" in agents
        assert "gemini" in agents

    def test_registry_get_existing(self):
        """Get returns AgentConfig for existing agent."""
        registry = AgentRegistry()

        config = registry.get("claude")

        assert config is not None
        assert config.name == "claude"

    def test_registry_get_nonexistent(self):
        """Get returns None for nonexistent agent."""
        registry = AgentRegistry()

        config = registry.get("nonexistent")

        assert config is None

    def test_registry_get_or_raise_existing(self):
        """get_or_raise returns AgentConfig for existing agent."""
        registry = AgentRegistry()

        config = registry.get_or_raise("claude")

        assert config.name == "claude"

    def test_registry_get_or_raise_nonexistent(self):
        """get_or_raise raises ValueError for nonexistent agent."""
        registry = AgentRegistry()

        with pytest.raises(ValueError, match="Unknown agent: 'nonexistent'"):
            registry.get_or_raise("nonexistent")

    def test_registry_list_agents_sorted(self):
        """list_agents returns sorted list."""
        registry = AgentRegistry()

        agents = registry.list_agents()

        assert agents == sorted(agents)

    def test_registry_get_default_skills_dir(self):
        """get_default_skills_dir returns default skills directory."""
        registry = AgentRegistry()

        skills_dir = registry.get_default_skills_dir()

        assert skills_dir == Path.home() / ".claude" / "skills"

    def test_registry_get_agents_with_home_support(self):
        """get_agents_with_home_support returns agents with user-level support."""
        registry = AgentRegistry()

        agents = registry.get_agents_with_home_support()

        assert "claude" in agents
        assert "opencode" in agents
        assert "codex" in agents
        assert "universal" in agents
        assert "gemini" in agents  # SKILZ-49: Gemini now has home support

    def test_registry_get_agents_by_native_support(self):
        """get_agents_by_native_support filters by support level."""
        registry = AgentRegistry()

        all_support = registry.get_agents_by_native_support("all")
        home_support = registry.get_agents_by_native_support("home")
        none_support = registry.get_agents_by_native_support("none")

        assert "claude" in all_support
        assert "codex" in all_support
        assert "copilot" in all_support  # SKILZ-54: Copilot has native support
        assert "opencode" in all_support  # OpenCode has full native support
        assert "gemini" in all_support  # SKILZ-49: Gemini has native support
        assert len(home_support) == 0  # No agents currently use "home" only
        assert "gemini" not in none_support  # Gemini moved from none to all

    def test_registry_loads_user_config(self, tmp_path):
        """Registry merges user configuration on top of built-ins."""
        config_file = tmp_path / "config.json"
        config_file.write_text(
            json.dumps(
                {
                    "agents": {
                        "claude": {
                            "display_name": "My Custom Claude",
                            "project_dir": ".my-claude/skills",
                            "default_mode": "symlink",
                        }
                    }
                }
            )
        )

        registry = AgentRegistry(config_path=config_file)

        claude = registry.get("claude")
        assert claude is not None
        assert claude.display_name == "My Custom Claude"
        assert claude.project_dir == Path(".my-claude/skills")

    def test_registry_ignores_invalid_user_config(self, tmp_path):
        """Registry ignores invalid user configuration entries."""
        config_file = tmp_path / "config.json"
        config_file.write_text(
            json.dumps(
                {
                    "agents": {
                        "invalid_agent": {
                            # Missing required fields
                            "display_name": "Invalid"
                        }
                    }
                }
            )
        )

        # Should not raise, just skip invalid entry
        registry = AgentRegistry(config_path=config_file)

        # Built-in agents should still work
        assert registry.get("claude") is not None


class TestSkillNameValidation:
    """Tests for skill name validation."""

    def test_valid_simple_name(self):
        """Simple lowercase name is valid."""
        result = validate_skill_name("pdf")

        assert result.is_valid is True
        assert result.normalized_name == "pdf"
        assert result.errors == []

    def test_valid_hyphenated_name(self):
        """Hyphenated name is valid."""
        result = validate_skill_name("web-scraper")

        assert result.is_valid is True
        assert result.normalized_name == "web-scraper"

    def test_valid_with_numbers(self):
        """Name with numbers is valid."""
        result = validate_skill_name("pdf2text")

        assert result.is_valid is True
        assert result.normalized_name == "pdf2text"

    def test_invalid_starts_with_number(self):
        """Name starting with number is invalid."""
        result = validate_skill_name("2pdf")

        assert result.is_valid is False
        error_msg = result.errors[0].lower()
        assert "must start with a letter" in error_msg or "must be lowercase" in error_msg

    def test_invalid_uppercase(self):
        """Uppercase is normalized to lowercase."""
        result = validate_skill_name("PDF")

        # NFKC normalization converts to lowercase
        assert result.normalized_name == "pdf"
        assert result.is_valid is True

    def test_invalid_consecutive_hyphens(self):
        """Consecutive hyphens are invalid."""
        result = validate_skill_name("web--scraper")

        assert result.is_valid is False

    def test_invalid_leading_hyphen(self):
        """Leading hyphen is invalid."""
        result = validate_skill_name("-pdf")

        assert result.is_valid is False

    def test_invalid_trailing_hyphen(self):
        """Trailing hyphen is invalid."""
        result = validate_skill_name("pdf-")

        assert result.is_valid is False

    def test_invalid_special_characters(self):
        """Special characters are invalid."""
        result = validate_skill_name("pdf@reader")

        assert result.is_valid is False

    def test_too_long_name(self):
        """Name exceeding 64 characters is invalid."""
        long_name = "a" * 65

        result = validate_skill_name(long_name)

        assert result.is_valid is False
        assert "exceeds 64 characters" in result.errors[0]

    def test_empty_name(self):
        """Empty name is invalid."""
        result = validate_skill_name("")

        assert result.is_valid is False
        assert "cannot be empty" in result.errors[0]

    def test_suggested_name_for_invalid(self):
        """Invalid names get a suggested correction."""
        result = validate_skill_name("PDF Reader")

        assert result.is_valid is False
        assert result.suggested_name == "pdf-reader"


class TestCheckSkillDirectoryName:
    """Tests for check_skill_directory_name function."""

    def test_matching_names(self, tmp_path):
        """Return True when directory matches expected name."""
        skill_dir = tmp_path / "pdf"
        skill_dir.mkdir()

        matches, suggested = check_skill_directory_name(skill_dir, "pdf")

        assert matches is True
        assert suggested is None

    def test_mismatched_names(self, tmp_path):
        """Return False with suggested path when names don't match."""
        skill_dir = tmp_path / "PDF"
        skill_dir.mkdir()

        matches, suggested = check_skill_directory_name(skill_dir, "pdf")

        assert matches is False
        assert suggested == str(tmp_path / "pdf")


class TestRenameSkillDirectory:
    """Tests for rename_skill_directory function."""

    def test_rename_success(self, tmp_path):
        """Successfully rename skill directory."""
        old_dir = tmp_path / "old-pdf-skill"
        old_dir.mkdir()
        (old_dir / "SKILL.md").touch()

        new_dir = rename_skill_directory(old_dir, "pdf-reader")

        assert new_dir == tmp_path / "pdf-reader"
        assert new_dir.exists()
        assert not old_dir.exists()
        assert (new_dir / "SKILL.md").exists()

    def test_rename_target_exists(self, tmp_path):
        """Raise FileExistsError if target already exists."""
        old_dir = tmp_path / "old-skill"
        old_dir.mkdir()
        target_dir = tmp_path / "new-skill"
        target_dir.mkdir()

        with pytest.raises(FileExistsError, match="already exists"):
            rename_skill_directory(old_dir, "new-skill")


class TestModuleSingleton:
    """Tests for module-level singleton."""

    def test_get_registry_returns_same_instance(self):
        """get_registry returns the same instance each time."""
        reset_registry()  # Clear any existing instance

        registry1 = get_registry()
        registry2 = get_registry()

        assert registry1 is registry2

    def test_reset_registry_clears_instance(self):
        """reset_registry clears the singleton."""
        reset_registry()

        registry1 = get_registry()
        reset_registry()
        registry2 = get_registry()

        # After reset, should be a new instance
        assert registry1 is not registry2

    def test_get_agent_choices(self):
        """get_agent_choices returns list of agent names."""
        reset_registry()

        choices = get_agent_choices()

        assert isinstance(choices, list)
        assert len(choices) >= 30  # Updated for new agents
        assert "claude" in choices
        assert "gemini" in choices


class TestNewAgents:
    """Tests for new agents added in Issues #46, #47, #49."""

    def test_qwen_agent_config(self):
        """Test Qwen Code agent configuration (Issue #46)."""
        registry = AgentRegistry()
        agent = registry.get("qwen")

        assert agent is not None
        assert agent.display_name == "Qwen Code"
        assert agent.project_dir == Path(".qwen") / "skills"
        assert agent.home_dir == Path.home() / ".qwen" / "skills"
        assert agent.supports_home is True
        assert agent.native_skill_support == "all"
        assert "QWEN.md" in agent.config_files

    def test_antigravity_agent_config(self):
        """Test Antigravity agent configuration (Issue #47)."""
        registry = AgentRegistry()
        agent = registry.get("antigravity")

        assert agent is not None
        assert agent.display_name == "Google Antigravity"
        assert agent.project_dir == Path(".agent") / "skills"
        assert agent.home_dir == Path.home() / ".gemini" / "antigravity" / "skills"
        assert agent.supports_home is True
        assert agent.native_skill_support == "all"
        assert agent.config_files == ()  # Native discovery

    def test_openhands_agent_config(self):
        """Test OpenHands agent configuration (Issue #49)."""
        registry = AgentRegistry()
        agent = registry.get("openhands")

        assert agent is not None
        assert agent.display_name == "OpenHands"
        assert agent.project_dir == Path(".openhands") / "skills"
        assert agent.home_dir == Path.home() / ".openhands" / "skills"
        assert agent.supports_home is True
        assert agent.native_skill_support == "all"

    def test_cline_agent_config(self):
        """Test Cline agent configuration (Issue #49)."""
        registry = AgentRegistry()
        agent = registry.get("cline")

        assert agent is not None
        assert agent.display_name == "Cline"
        assert agent.project_dir == Path(".cline") / "skills"
        assert agent.home_dir == Path.home() / ".cline" / "skills"
        assert agent.supports_home is True
        assert agent.native_skill_support == "all"

    def test_goose_agent_config(self):
        """Test Goose agent configuration (Issue #49)."""
        registry = AgentRegistry()
        agent = registry.get("goose")

        assert agent is not None
        assert agent.display_name == "Goose"
        assert agent.project_dir == Path(".goose") / "skills"
        assert agent.home_dir == Path.home() / ".config" / "goose" / "skills"
        assert agent.supports_home is True
        assert agent.native_skill_support == "all"

    def test_roo_agent_config(self):
        """Test Roo Code agent configuration (Issue #49)."""
        registry = AgentRegistry()
        agent = registry.get("roo")

        assert agent is not None
        assert agent.display_name == "Roo Code"
        assert agent.project_dir == Path(".roo") / "skills"
        assert agent.home_dir == Path.home() / ".roo" / "skills"
        assert agent.supports_home is True
        assert agent.native_skill_support == "all"

    def test_kilo_agent_config(self):
        """Test Kilo Code agent configuration (Issue #49)."""
        registry = AgentRegistry()
        agent = registry.get("kilo")

        assert agent is not None
        assert agent.display_name == "Kilo Code"
        assert agent.project_dir == Path(".kilocode") / "skills"
        assert agent.home_dir == Path.home() / ".kilocode" / "skills"
        assert agent.supports_home is True
        assert agent.native_skill_support == "all"

    def test_trae_agent_config(self):
        """Test Trae agent configuration (Issue #49)."""
        registry = AgentRegistry()
        agent = registry.get("trae")

        assert agent is not None
        assert agent.display_name == "Trae"
        assert agent.project_dir == Path(".trae") / "skills"
        assert agent.home_dir == Path.home() / ".trae" / "skills"
        assert agent.supports_home is True
        assert agent.native_skill_support == "all"

    def test_droid_agent_config(self):
        """Test Droid agent configuration (Issue #49)."""
        registry = AgentRegistry()
        agent = registry.get("droid")

        assert agent is not None
        assert agent.display_name == "Droid"
        assert agent.project_dir == Path(".factory") / "skills"
        assert agent.home_dir == Path.home() / ".factory" / "skills"
        assert agent.supports_home is True
        assert agent.native_skill_support == "all"

    def test_clawdbot_agent_config(self):
        """Test Clawdbot agent configuration (Issue #49)."""
        registry = AgentRegistry()
        agent = registry.get("clawdbot")

        assert agent is not None
        assert agent.display_name == "Clawdbot"
        assert agent.project_dir == Path("skills")  # Unique: project root
        assert agent.home_dir == Path.home() / ".clawdbot" / "skills"
        assert agent.supports_home is True
        assert agent.native_skill_support == "all"

    def test_kiro_cli_agent_config(self):
        """Test Kiro CLI agent configuration (Issue #49)."""
        registry = AgentRegistry()
        agent = registry.get("kiro-cli")

        assert agent is not None
        assert agent.display_name == "Kiro CLI"
        assert agent.project_dir == Path(".kiro") / "skills"
        assert agent.home_dir == Path.home() / ".kiro" / "skills"
        assert agent.supports_home is True
        assert agent.native_skill_support == "all"

    def test_pi_agent_config(self):
        """Test Pi agent configuration (Issue #49)."""
        registry = AgentRegistry()
        agent = registry.get("pi")

        assert agent is not None
        assert agent.display_name == "Pi"
        assert agent.project_dir == Path(".pi") / "skills"
        assert agent.home_dir == Path.home() / ".pi" / "agent" / "skills"
        assert agent.supports_home is True
        assert agent.native_skill_support == "all"

    def test_neovate_agent_config(self):
        """Test Neovate agent configuration (Issue #49)."""
        registry = AgentRegistry()
        agent = registry.get("neovate")

        assert agent is not None
        assert agent.display_name == "Neovate"
        assert agent.project_dir == Path(".neovate") / "skills"
        assert agent.home_dir == Path.home() / ".neovate" / "skills"
        assert agent.supports_home is True
        assert agent.native_skill_support == "all"

    def test_updated_agents_have_native_support(self):
        """Test that updated agents now have native support."""
        registry = AgentRegistry()

        # Test Cursor (updated from bridged to native)
        cursor = registry.get("cursor")
        assert cursor is not None
        assert cursor.project_dir == Path(".cursor") / "skills"
        assert cursor.home_dir == Path.home() / ".cursor" / "skills"
        assert cursor.supports_home is True
        assert cursor.native_skill_support == "all"

        # Test Windsurf (updated from bridged to native)
        windsurf = registry.get("windsurf")
        assert windsurf is not None
        assert windsurf.project_dir == Path(".windsurf") / "skills"
        assert windsurf.home_dir == Path.home() / ".codeium" / "windsurf" / "skills"
        assert windsurf.supports_home is True
        assert windsurf.native_skill_support == "all"

        # Test GitHub Copilot (added global support)
        copilot = registry.get("copilot")
        assert copilot is not None
        assert copilot.project_dir == Path(".github") / "skills"
        assert copilot.home_dir == Path.home() / ".copilot" / "skills"
        assert copilot.supports_home is True
        assert copilot.native_skill_support == "all"

    def test_all_new_agents_are_registered(self):
        """Test that all new agents from Issues #46, #47, #49 are registered."""
        registry = AgentRegistry()
        agents = registry.list_agents()

        # New agents from the issues
        new_agents = [
            "antigravity",  # Issue #47
            "openhands",
            "cline",
            "goose",
            "roo",
            "kilo",
            "trae",
            "droid",  # Issue #49
            "clawdbot",
            "kiro-cli",
            "pi",
            "neovate",
            "zencoder",
            "amp",
            "qoder",
            "command-code",  # Issue #49
        ]

        for agent_name in new_agents:
            assert agent_name in agents, f"Agent '{agent_name}' not found in registry"

        # Verify total count is at least 30
        assert len(agents) >= 30, f"Expected at least 30 agents, got {len(agents)}"
