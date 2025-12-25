# Phase 6: Implementation Plan - Agent Registry System

## Architecture Overview

### New Files
| File | Purpose |
|------|---------|
| `src/skilz/agent_registry.py` | AgentConfig dataclass, registry loading, built-in defaults |
| `tests/test_agent_registry.py` | Agent registry unit tests |

### Modified Files
| File | Change |
|------|--------|
| `src/skilz/agents.py` | Delegate to registry, maintain backward compatibility |
| `src/skilz/cli.py` | Dynamic `--agent` choices from registry |
| `src/skilz/config.py` | Add registry loading from `~/.config/skilz/config.json` |
| `src/skilz/commands/install_cmd.py` | Pass agent config to installer |
| `src/skilz/commands/list_cmd.py` | Use display names |

## Design Decisions

### D1: Frozen Dataclass for AgentConfig
**Decision:** Use `@dataclass(frozen=True)` for immutability
**Rationale:** Prevents accidental modification, enables hashability for caching

### D2: Registry as Module-Level Singleton
**Decision:** Load registry once at module import, cache globally
**Rationale:** Avoids repeated file I/O, ensures consistency across commands

### D3: Built-in Defaults with User Override
**Decision:** Merge user config on top of built-in defaults
**Rationale:** Users only need to specify what they want to change

### D4: Backward Compatibility via Delegation
**Decision:** Keep `agents.py` API, delegate to registry internally
**Rationale:** Zero breaking changes for existing code

### D5: AgentType as Dynamic Literal
**Decision:** Generate `AgentType` from registry keys at runtime
**Rationale:** Enables custom agents without code changes

### D6: Path Expansion at Load Time
**Decision:** Expand `~` to full path when loading registry
**Rationale:** Consistent path handling throughout application

## Component Details

### Agent Registry Module (`agent_registry.py`)

```python
from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal

@dataclass(frozen=True)
class AgentConfig:
    name: str
    display_name: str
    home_dir: Path | None
    project_dir: Path
    config_files: tuple[str, ...]
    supports_home: bool
    default_mode: Literal["copy", "symlink"]
    native_skill_support: Literal["all", "home", "none"]
    uses_folder_rules: bool = False
    invocation: str | None = None

# Built-in defaults
BUILTIN_AGENTS: dict[str, AgentConfig] = {
    "claude": AgentConfig(
        name="claude",
        display_name="Claude Code",
        home_dir=Path.home() / ".claude" / "skills",
        project_dir=Path(".claude") / "skills",
        config_files=("CLAUDE.md",),
        supports_home=True,
        default_mode="copy",
        native_skill_support="all",
    ),
    # ... 13 more agents
}

class AgentRegistry:
    """Manages agent configurations with user customization."""

    def __init__(self, config_path: Path | None = None):
        self._agents: dict[str, AgentConfig] = {}
        self._load(config_path)

    def _load(self, config_path: Path | None) -> None:
        # Start with built-in defaults
        self._agents = dict(BUILTIN_AGENTS)

        # Merge user config if exists
        if config_path and config_path.exists():
            user_config = self._load_user_config(config_path)
            self._merge_user_config(user_config)

    def get(self, name: str) -> AgentConfig | None:
        return self._agents.get(name)

    def get_or_raise(self, name: str) -> AgentConfig:
        if agent := self._agents.get(name):
            return agent
        raise ValueError(f"Unknown agent: {name}")

    def list_agents(self) -> list[str]:
        return list(self._agents.keys())

    def get_default_skills_dir(self) -> Path:
        return self._default_skills_dir

# Module-level singleton
_registry: AgentRegistry | None = None

def get_registry() -> AgentRegistry:
    global _registry
    if _registry is None:
        _registry = AgentRegistry(get_config_path())
    return _registry
```

### Config Module Extension (`config.py`)

Add to existing config.py:

```python
REGISTRY_CONFIG_PATH = Path.home() / ".config" / "skilz" / "config.json"

def get_registry_config_path() -> Path:
    """Get path to agent registry config file."""
    return REGISTRY_CONFIG_PATH

def load_registry_config() -> dict | None:
    """Load agent registry from config file if exists."""
    path = get_registry_config_path()
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text())
    except (json.JSONDecodeError, OSError):
        return None
```

### Agents Module Refactoring (`agents.py`)

```python
# Keep existing types for backward compatibility
AgentType = Literal["claude", "opencode"]  # Will be extended dynamically

# Backward-compatible functions that delegate to registry
def get_agent_paths() -> dict[str, dict[str, Path]]:
    """Get agent paths - delegates to registry."""
    from skilz.agent_registry import get_registry
    registry = get_registry()

    result = {}
    for name in registry.list_agents():
        agent = registry.get(name)
        if agent.supports_home:
            result[name] = {
                "user": agent.home_dir,
                "project": agent.project_dir,
            }
        else:
            result[name] = {
                "project": agent.project_dir,
            }
    return result

def get_agent_display_name(agent: str) -> str:
    """Get display name for agent."""
    from skilz.agent_registry import get_registry
    if config := get_registry().get(agent):
        return config.display_name
    return agent
```

### CLI Dynamic Choices (`cli.py`)

```python
def get_agent_choices() -> list[str]:
    """Get list of valid agent names from registry."""
    try:
        from skilz.agent_registry import get_registry
        return get_registry().list_agents()
    except ImportError:
        return ["claude", "opencode"]  # Fallback

def create_parser() -> argparse.ArgumentParser:
    # ...
    install_parser.add_argument(
        "--agent",
        choices=get_agent_choices(),
        default=None,
        help="Target agent (auto-detected if not specified)",
    )
```

## Built-in Agent Registry

| Agent | Home Dir | Project Dir | Native Support | Default Mode |
|-------|----------|-------------|----------------|--------------|
| claude | ~/.claude/skills | .claude/skills | all | copy |
| opencode | ~/.config/opencode/skills | .skilz/skills | home | copy |
| codex | ~/.codex/skills | .codex/skills | all | copy |
| gemini | - | .skilz/skills | none | symlink |
| copilot | - | .github/copilot/skills | none | symlink |
| aider | - | .skills/skills | none | symlink |
| cursor | - | .skills/skills | none | symlink |
| windsurf | - | .skills/skills | none | symlink |
| qwen | - | .skills/skills | none | symlink |
| crush | - | .skills/skills | none | symlink |
| kimi | - | .skills/skills | none | symlink |
| plandex | - | .skills/skills | none | symlink |
| zed | - | .skills/skills | none | symlink |
| universal | ~/.skilz/skills | .skilz/skills | - | copy |

## Testing Strategy

### Unit Tests (`test_agent_registry.py`)

```python
class TestAgentConfig:
    def test_frozen_dataclass(self):
        """AgentConfig is immutable."""
        config = AgentConfig(...)
        with pytest.raises(FrozenInstanceError):
            config.name = "other"

    def test_path_expansion(self):
        """Home dir expands ~ correctly."""
        config = create_agent_config("~/.claude/skills")
        assert config.home_dir == Path.home() / ".claude" / "skills"

class TestAgentRegistry:
    def test_builtin_agents(self):
        """All 14 built-in agents present."""
        registry = AgentRegistry()
        assert len(registry.list_agents()) == 14
        assert "claude" in registry.list_agents()
        assert "gemini" in registry.list_agents()

    def test_user_config_override(self):
        """User config overrides built-in values."""
        # Create temp config file
        registry = AgentRegistry(config_path=tmp_config)
        claude = registry.get("claude")
        assert claude.home_dir == custom_path

    def test_get_or_raise_unknown(self):
        """get_or_raise raises for unknown agent."""
        registry = AgentRegistry()
        with pytest.raises(ValueError, match="Unknown agent"):
            registry.get_or_raise("nonexistent")

    def test_backward_compatibility(self):
        """Existing agents.py functions still work."""
        from skilz.agents import get_agent_paths, detect_agent
        paths = get_agent_paths()
        assert "claude" in paths
        assert "opencode" in paths
```

### Integration Tests

```python
def test_cli_shows_all_agents():
    """CLI help shows all agent choices."""
    result = subprocess.run(["skilz", "install", "--help"], capture_output=True)
    assert "gemini" in result.stdout.decode()
    assert "cursor" in result.stdout.decode()

def test_install_with_new_agent():
    """Can install skill for new agents."""
    result = subprocess.run(
        ["skilz", "install", "test/skill", "--agent", "gemini", "--project"],
        capture_output=True
    )
    assert result.returncode == 0
```

### Coverage Target
90%+ coverage on agent_registry.py

## Implementation Order

1. **Step 1:** Create `agent_registry.py` with AgentConfig dataclass
2. **Step 2:** Add built-in agent definitions (all 14 agents)
3. **Step 3:** Implement AgentRegistry class with loading logic
4. **Step 4:** Extend `config.py` with registry config loading
5. **Step 5:** Refactor `agents.py` to delegate to registry
6. **Step 6:** Update `cli.py` for dynamic agent choices
7. **Step 7:** Write tests for agent_registry module
8. **Step 8:** Update command handlers for new agents
9. **Step 9:** Run full test suite, verify backward compatibility

## Rollout Plan

1. **Phase 6a:** Create agent_registry.py with core logic (no behavior change)
2. **Phase 6b:** Integrate registry with agents.py (delegates internally)
3. **Phase 6c:** Update CLI for dynamic choices (visible change)
4. **Phase 6d:** Add user config support (optional feature)
5. **Phase 6e:** Update documentation
