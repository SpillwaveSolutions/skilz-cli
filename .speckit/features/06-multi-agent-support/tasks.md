# Phase 6: Tasks - Agent Registry System

## Status Summary

| Phase | Status | Tests |
|-------|--------|-------|
| 6a: AgentConfig dataclass | ⬜ Pending | - |
| 6b: Built-in agent definitions | ⬜ Pending | - |
| 6c: AgentRegistry class | ⬜ Pending | - |
| 6d: Config integration | ⬜ Pending | - |
| 6e: Refactor agents.py | ⬜ Pending | - |
| 6f: Dynamic CLI choices | ⬜ Pending | - |
| 6g: Tests & validation | ⬜ Pending | - |
| **Total** | **⬜ Pending** | **0 tests** |

---

## Phase 6a: AgentConfig Dataclass

- [ ] Create `src/skilz/agent_registry.py`
- [ ] Define `AgentConfig` frozen dataclass with fields:
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
- [ ] Add `from_dict()` class method for JSON loading
- [ ] Add path expansion logic for `~` in paths
- [ ] Add basic validation (required fields, valid enums)

**Files:** `src/skilz/agent_registry.py`

**Estimated:** 1 hour

---

## Phase 6b: Built-in Agent Definitions

- [ ] Define `BUILTIN_AGENTS` dictionary with all 14 agents:
  - [ ] claude (home + project, copy, native=all)
  - [ ] opencode (home + project, copy, native=home)
  - [ ] codex (home + project, copy, native=all)
  - [ ] gemini (project only, symlink, native=none)
  - [ ] copilot (project only, symlink, native=none)
  - [ ] aider (project only, symlink, native=none)
  - [ ] cursor (project only, symlink, native=none, folder_rules=true)
  - [ ] windsurf (project only, symlink, native=none)
  - [ ] qwen (project only, symlink, native=none)
  - [ ] crush (project only, symlink, native=none)
  - [ ] kimi (project only, symlink, native=none)
  - [ ] plandex (project only, symlink, native=none)
  - [ ] zed (project only, symlink, native=none)
  - [ ] universal (home + project, copy)
- [ ] Define `DEFAULT_SKILLS_DIR` constant (defaults to ~/.claude/skills)
- [ ] Verify all paths match docs/plans/support_more_code_agents.md

**Files:** `src/skilz/agent_registry.py`

**Estimated:** 30 minutes

---

## Phase 6c: AgentRegistry Class

- [ ] Create `AgentRegistry` class
- [ ] Implement `__init__(config_path: Path | None = None)`
- [ ] Implement `_load(config_path)` - load and merge configs
- [ ] Implement `_load_user_config(path)` - parse JSON file
- [ ] Implement `_merge_user_config(user_config)` - override built-ins
- [ ] Implement `get(name: str) -> AgentConfig | None`
- [ ] Implement `get_or_raise(name: str) -> AgentConfig`
- [ ] Implement `list_agents() -> list[str]`
- [ ] Implement `get_default_skills_dir() -> Path`
- [ ] Create module-level singleton `_registry`
- [ ] Implement `get_registry() -> AgentRegistry` function
- [ ] Add `reset_registry()` for testing

**Files:** `src/skilz/agent_registry.py`

**Estimated:** 1.5 hours

---

## Phase 6d: Config Integration

- [ ] Add `REGISTRY_CONFIG_PATH` to `config.py`
- [ ] Implement `get_registry_config_path() -> Path`
- [ ] Implement `load_registry_config() -> dict | None`
- [ ] Handle JSON parse errors gracefully
- [ ] Handle missing file gracefully
- [ ] Update `agent_registry.py` to use config functions

**Files:** `src/skilz/config.py`, `src/skilz/agent_registry.py`

**Estimated:** 30 minutes

---

## Phase 6e: Refactor agents.py

- [ ] Keep `AgentType` for backward compatibility
- [ ] Keep `DEFAULT_AGENT_PATHS` as fallback
- [ ] Keep `AGENT_PATHS` alias
- [ ] Refactor `get_agent_paths()` to delegate to registry
- [ ] Refactor `detect_agent()` to use registry
- [ ] Refactor `get_skills_dir()` to use registry
- [ ] Refactor `ensure_skills_dir()` to use registry
- [ ] Update `get_agent_display_name()` to use registry
- [ ] Add try/except for ImportError fallback
- [ ] Verify all existing tests still pass

**Files:** `src/skilz/agents.py`

**Estimated:** 1 hour

---

## Phase 6f: Dynamic CLI Choices

- [ ] Add `get_agent_choices() -> list[str]` function
- [ ] Update install command `--agent` choices
- [ ] Update list command `--agent` choices
- [ ] Update update command `--agent` choices
- [ ] Update remove command `--agent` choices
- [ ] Update config command if applicable
- [ ] Verify help text shows all agents
- [ ] Add fallback to ["claude", "opencode"] if registry fails

**Files:** `src/skilz/cli.py`

**Estimated:** 45 minutes

---

## Phase 6g: Tests & Validation

### Unit Tests

- [ ] Create `tests/test_agent_registry.py`
- [ ] Test `AgentConfig` frozen immutability
- [ ] Test `AgentConfig.from_dict()` with valid data
- [ ] Test `AgentConfig.from_dict()` with missing fields
- [ ] Test `AgentConfig.from_dict()` with invalid enum values
- [ ] Test path expansion for `~`
- [ ] Test `AgentRegistry` with no config file
- [ ] Test `AgentRegistry` with valid config file
- [ ] Test `AgentRegistry` with corrupted config file
- [ ] Test `AgentRegistry.get()` for existing agent
- [ ] Test `AgentRegistry.get()` for unknown agent
- [ ] Test `AgentRegistry.get_or_raise()` success
- [ ] Test `AgentRegistry.get_or_raise()` failure
- [ ] Test `AgentRegistry.list_agents()` returns all 14
- [ ] Test user config overrides built-in values
- [ ] Test `get_registry()` singleton behavior
- [ ] Test `reset_registry()` clears singleton

### Integration Tests

- [ ] Test `agents.py` backward compatibility
- [ ] Test `get_agent_paths()` returns all agents
- [ ] Test `detect_agent()` still works
- [ ] Test CLI help shows all agent choices
- [ ] Test `skilz install --agent gemini` is valid
- [ ] Test `skilz list --agent cursor` is valid

### Coverage

- [ ] Verify 90%+ coverage on agent_registry.py
- [ ] Run full test suite: `task test`
- [ ] Verify no regressions in existing tests

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

- [ ] All 14 agents listed in `skilz install --help`
- [ ] `skilz install skill --agent gemini --project` works
- [ ] `skilz list --agent cursor` works
- [ ] Existing `skilz install skill` still defaults to claude
- [ ] Existing `skilz install skill --agent opencode` works
- [ ] No performance regression (CLI startup <100ms)
- [ ] 90%+ test coverage on new code
- [ ] All 239+ existing tests still pass
- [ ] Code passes `task lint`
- [ ] Code passes `task check`

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
