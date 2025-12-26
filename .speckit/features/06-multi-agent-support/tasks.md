# Phase 6: Tasks - Agent Registry System

## Status Summary

| Phase | Status | Tests |
|-------|--------|-------|
| 6a: AgentConfig dataclass | ✅ Complete | 8 |
| 6b: Built-in agent definitions | ✅ Complete | 6 |
| 6c: AgentRegistry class | ✅ Complete | 12 |
| 6d: Config integration | ✅ Complete | 2 |
| 6e: Refactor agents.py | ✅ Complete | 5 |
| 6f: Dynamic CLI choices | ✅ Complete | 3 |
| 6g: Tests & validation | ✅ Complete | 5 |
| **Total** | **✅ Complete** | **41 tests** |

---

## Phase 6a: AgentConfig Dataclass

- [x] Create `src/skilz/agent_registry.py`
- [x] Define `AgentConfig` frozen dataclass with fields:
  - `name: str`
  - `display_name: str`
  - `home_dir: Path | None`
  - `project_dir: Path`
  - `config_files: tuple[str, ...]`
  - `supports_home: bool`
  - `default_mode: Literal["copy", "symlink"]`
  - `native_skill_support: Literal["all", "home", "none"]`
  - `uses_folder_rules: bool = False`
  - `invocation: str | None = None`
- [x] Add `from_dict()` class method for JSON loading
- [x] Add path expansion logic for `~` in paths
- [x] Add basic validation (required fields, valid enums)

**Files:** `src/skilz/agent_registry.py`

**Estimated:** 1 hour

---

## Phase 6b: Built-in Agent Definitions

- [x] Define `BUILTIN_AGENTS` dictionary with all 14 agents:
  - [x] claude (home + project, copy, native=all)
  - [x] opencode (home + project, copy, native=home)
  - [x] codex (home + project, copy, native=all)
  - [x] gemini (project only, symlink, native=none)
  - [x] copilot (project only, symlink, native=none)
  - [x] aider (project only, symlink, native=none)
  - [x] cursor (project only, symlink, native=none, folder_rules=true)
  - [x] windsurf (project only, symlink, native=none)
  - [x] qwen (project only, symlink, native=none)
  - [x] crush (project only, symlink, native=none)
  - [x] kimi (project only, symlink, native=none)
  - [x] plandex (project only, symlink, native=none)
  - [x] zed (project only, symlink, native=none)
  - [x] universal (home + project, copy)
- [x] Define `DEFAULT_SKILLS_DIR` constant (defaults to ~/.claude/skills)
- [x] Verify all paths match docs/plans/support_more_code_agents.md

**Files:** `src/skilz/agent_registry.py`

**Estimated:** 30 minutes

---

## Phase 6c: AgentRegistry Class

- [x] Create `AgentRegistry` class
- [x] Implement `__init__(config_path: Path | None = None)`
- [x] Implement `_load(config_path)` - load and merge configs
- [x] Implement `_load_user_config(path)` - parse JSON file
- [x] Implement `_merge_user_config(user_config)` - override built-ins
- [x] Implement `get(name: str) -> AgentConfig | None`
- [x] Implement `get_or_raise(name: str) -> AgentConfig`
- [x] Implement `list_agents() -> list[str]`
- [x] Implement `get_default_skills_dir() -> Path`
- [x] Create module-level singleton `_registry`
- [x] Implement `get_registry() -> AgentRegistry` function
- [x] Add `reset_registry()` for testing

**Files:** `src/skilz/agent_registry.py`

**Estimated:** 1.5 hours

---

## Phase 6d: Config Integration

- [x] Add `REGISTRY_CONFIG_PATH` to `config.py`
- [x] Implement `get_registry_config_path() -> Path`
- [x] Implement `load_registry_config() -> dict | None`
- [x] Handle JSON parse errors gracefully
- [x] Handle missing file gracefully
- [x] Update `agent_registry.py` to use config functions

**Files:** `src/skilz/config.py`, `src/skilz/agent_registry.py`

**Estimated:** 30 minutes

---

## Phase 6e: Refactor agents.py

- [x] Keep `AgentType` for backward compatibility
- [x] Keep `DEFAULT_AGENT_PATHS` as fallback
- [x] Keep `AGENT_PATHS` alias
- [x] Refactor `get_agent_paths()` to delegate to registry
- [x] Refactor `detect_agent()` to use registry
- [x] Refactor `get_skills_dir()` to use registry
- [x] Refactor `ensure_skills_dir()` to use registry
- [x] Update `get_agent_display_name()` to use registry
- [x] Add try/except for ImportError fallback
- [x] Verify all existing tests still pass

**Files:** `src/skilz/agents.py`

**Estimated:** 1 hour

---

## Phase 6f: Dynamic CLI Choices

- [x] Add `get_agent_choices() -> list[str]` function
- [x] Update install command `--agent` choices
- [x] Update list command `--agent` choices
- [x] Update update command `--agent` choices
- [x] Update remove command `--agent` choices
- [x] Update config command if applicable
- [x] Verify help text shows all agents
- [x] Add fallback to ["claude", "opencode"] if registry fails

**Files:** `src/skilz/cli.py`

**Estimated:** 45 minutes

---

## Phase 6g: Tests & Validation

### Unit Tests

- [x] Create `tests/test_agent_registry.py`
- [x] Test `AgentConfig` frozen immutability
- [x] Test `AgentConfig.from_dict()` with valid data
- [x] Test `AgentConfig.from_dict()` with missing fields
- [x] Test `AgentConfig.from_dict()` with invalid enum values
- [x] Test path expansion for `~`
- [x] Test `AgentRegistry` with no config file
- [x] Test `AgentRegistry` with valid config file
- [x] Test `AgentRegistry` with corrupted config file
- [x] Test `AgentRegistry.get()` for existing agent
- [x] Test `AgentRegistry.get()` for unknown agent
- [x] Test `AgentRegistry.get_or_raise()` success
- [x] Test `AgentRegistry.get_or_raise()` failure
- [x] Test `AgentRegistry.list_agents()` returns all 14
- [x] Test user config overrides built-in values
- [x] Test `get_registry()` singleton behavior
- [x] Test `reset_registry()` clears singleton

### Integration Tests

- [x] Test `agents.py` backward compatibility
- [x] Test `get_agent_paths()` returns all agents
- [x] Test `detect_agent()` still works
- [x] Test CLI help shows all agent choices
- [x] Test `skilz install --agent gemini` is valid
- [x] Test `skilz list --agent cursor` is valid

### Coverage

- [x] Verify 90%+ coverage on agent_registry.py
- [x] Run full test suite: `task test`
- [x] Verify no regressions in existing tests

**Files:** `tests/test_agent_registry.py`, existing test files

**Estimated:** 2 hours

---

## Test Coverage Target

| Test File | Tests Expected |
|-----------|----------------|
| test_agent_registry.py | ~25 |
| test_agents.py (additions) | ~5 |
| test_cli.py (additions) | ~5 |
| **Total New** | **~35** |

---

## Verification Checklist

Before marking complete:

- [x] All 14 agents listed in `skilz install --help`
- [x] `skilz install skill --agent gemini --project` works
- [x] `skilz list --agent cursor` works
- [x] Existing `skilz install skill` still defaults to claude
- [x] Existing `skilz install skill --agent opencode` works
- [x] No performance regression (CLI startup <100ms)
- [x] 90%+ test coverage on new code
- [x] All 254 existing tests still pass (295 total with 41 new)
- [x] Code passes `task lint`
- [x] Code passes `task check`

---

## Estimated Total Time

| Phase | Time |
|-------|------|
| 6a: AgentConfig dataclass | 1h |
| 6b: Built-in definitions | 0.5h |
| 6c: AgentRegistry class | 1.5h |
| 6d: Config integration | 0.5h |
| 6e: Refactor agents.py | 1h |
| 6f: Dynamic CLI choices | 0.75h |
| 6g: Tests & validation | 2h |
| **Total** | **~7-8 hours** |
