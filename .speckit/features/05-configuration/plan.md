# Phase 5: Implementation Plan

## Architecture Overview

### New Files
| File | Purpose |
|------|---------|
| `src/skilz/config.py` | Config loading, saving, env var handling |
| `src/skilz/completion.py` | Shell completion scripts and installation |
| `src/skilz/commands/config_cmd.py` | `skilz config` command handler |
| `tests/test_config.py` | Config module tests |
| `tests/test_config_cmd.py` | Config command tests |
| `tests/test_completion.py` | Completion module tests |

### Modified Files
| File | Change |
|------|--------|
| `src/skilz/cli.py` | Add `-y` flag, `config` subcommand, improve help |
| `src/skilz/agents.py` | Use config for paths, check agent_default |
| `src/skilz/commands/remove_cmd.py` | Check `yes_all` flag |
| `docs/USER_MANUAL.md` | Add configuration documentation |

## Design Decisions

### D1: Config File Location
**Decision:** Use `~/.config/skilz/settings.json`
**Rationale:** Follows XDG Base Directory Specification

### D2: JSON Key Format
**Decision:** Use snake_case for JSON keys
**Rationale:** Consistent with Python conventions and easier to type

### D3: Override Hierarchy
**Decision:** defaults < file < env < CLI
**Rationale:** Most specific wins, CLI always has final say

### D4: Only Save Non-Defaults
**Decision:** Only persist values that differ from defaults
**Rationale:** Keeps config file minimal, changes transparent

### D5: Lazy Imports
**Decision:** Import config module inside functions
**Rationale:** Prevents circular imports, allows graceful fallback

## Component Details

### Config Module (`config.py`)
```python
CONFIG_PATH = Path.home() / ".config" / "skilz" / "settings.json"

DEFAULTS = {
    "claude_code_home": str(Path.home() / ".claude"),
    "open_code_home": str(Path.home() / ".config" / "opencode"),
    "agent_default": None,
}

ENV_VARS = {
    "claude_code_home": "CLAUDE_CODE_HOME",
    "open_code_home": "OPEN_CODE_HOME",
    "agent_default": "AGENT_DEFAULT",
}
```

Key functions:
- `load_config()` - Load from file, merge with defaults
- `get_effective_config()` - Apply env overrides
- `save_config()` - Save non-default values
- `get_config_sources()` - Show all sources for display
- `get_claude_home()`, `get_opencode_home()` - Helper functions

### Agents Integration
Modify `agents.py` to use dynamic paths:
```python
def get_agent_paths() -> dict:
    from skilz.config import get_claude_home, get_opencode_home
    return {
        "claude": {"user": get_claude_home() / "skills", ...},
        "opencode": {"user": get_opencode_home() / "skills", ...},
    }

def detect_agent() -> AgentType:
    from skilz.config import get_default_agent
    if (default := get_default_agent()):
        return default
    # ... existing detection logic
```

### Shell Completion
Two completion scripts embedded as strings:
- `ZSH_COMPLETION` - Uses `_arguments` and `_describe`
- `BASH_COMPLETION` - Uses `compgen` and `complete -F`

Installation modifies shell RC files with safeguards against duplicates.

## Testing Strategy

### Unit Tests
- Config loading with missing/corrupted files
- Environment variable overrides
- Save only non-default values
- Helper functions return correct types

### Integration Tests
- Agent paths use config values
- detect_agent respects agent_default
- CLI parses new flags correctly

### Coverage Target
80%+ coverage on new code (matching project standard)

## Rollout Plan

1. **Phase 5a:** Add `-y` flag and fix help (backwards compatible)
2. **Phase 5b:** Add config module (no behavior change without config)
3. **Phase 5c:** Integrate config with agents (uses defaults if no config)
4. **Phase 5d:** Add config command (new functionality)
5. **Phase 5e:** Add shell completion (optional enhancement)
6. **Phase 5f:** Update documentation
