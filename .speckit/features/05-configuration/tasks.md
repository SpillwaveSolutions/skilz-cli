# Phase 5: Tasks

## Status Summary

| Phase | Status | Tests |
|-------|--------|-------|
| 5a: Global -y flag | ✅ Complete | 6 tests |
| 5b: Config module | ✅ Complete | 22 tests |
| 5c: Agent integration | ✅ Complete | 6 tests |
| 5d: Config command | ✅ Complete | 20 tests |
| 5e: Shell completion | ✅ Complete | 21 tests |
| 5f: Documentation | ✅ Complete | - |
| **Total** | **✅ Complete** | **75 new tests** |

---

## Phase 5a: Global -y Flag & Help Fix

- [x] Add `-y, --yes-all` to global parser in `cli.py`
- [x] Use `dest="yes_all"` to avoid conflict with remove's `-y`
- [x] Update `remove_cmd.py` to check `yes_all` in addition to `yes`
- [x] Update epilog to show `--agent` examples
- [x] Add "Common options" section to help
- [x] Add tests for new flag parsing
- [x] Add tests for yes_all behavior in remove

**Files:** `cli.py`, `remove_cmd.py`, `test_cli.py`, `test_remove_cmd.py`

---

## Phase 5b: Core Config Module

- [x] Create `src/skilz/config.py`
- [x] Define `CONFIG_DIR`, `CONFIG_PATH` constants
- [x] Define `DEFAULTS` dictionary
- [x] Define `ENV_VARS` mapping
- [x] Implement `load_config()` - load from file with defaults
- [x] Implement `get_effective_config()` - apply env overrides
- [x] Implement `save_config()` - save non-default values
- [x] Implement `get_config_sources()` - for display
- [x] Implement helper functions: `get_claude_home()`, `get_opencode_home()`, `get_default_agent()`
- [x] Implement `config_exists()` utility
- [x] Create `tests/test_config.py`
- [x] Test file loading, missing file, corrupted file
- [x] Test env var overrides
- [x] Test save only non-defaults
- [x] Test all helper functions

**Files:** `config.py`, `test_config.py`

---

## Phase 5c: Integrate Config with Agents

- [x] Add `get_agent_paths()` function to `agents.py`
- [x] Use lazy import of config module
- [x] Modify `get_skills_dir()` to use `get_agent_paths()`
- [x] Modify `detect_agent()` to check `get_default_agent()` first
- [x] Keep `DEFAULT_AGENT_PATHS` as fallback
- [x] Keep `AGENT_PATHS` alias for backwards compatibility
- [x] Add config integration tests to `test_agents.py`

**Files:** `agents.py`, `test_agents.py`

---

## Phase 5d: Config Command

- [x] Create `src/skilz/commands/config_cmd.py`
- [x] Implement `format_value()` for display formatting
- [x] Implement `prompt_value()` for interactive input
- [x] Implement `prompt_choice()` for choice prompts
- [x] Implement `cmd_config_show()` - display configuration
- [x] Implement `cmd_config_init()` - interactive setup
- [x] Handle `-y` flag for non-interactive init
- [x] Add config subparser to `cli.py`
- [x] Add handler in `main()` function
- [x] Create `tests/test_config_cmd.py`
- [x] Test show command output
- [x] Test init with -y flag
- [x] Test interactive init
- [x] Add CLI parsing tests

**Files:** `config_cmd.py`, `cli.py`, `test_config_cmd.py`, `test_cli.py`

---

## Phase 5e: Shell Completion

- [x] Create `src/skilz/completion.py`
- [x] Define `ZSH_COMPLETION` script
- [x] Define `BASH_COMPLETION` script
- [x] Implement `get_shell_type()` - detect current shell
- [x] Implement `get_completion_script()` - get script for shell
- [x] Implement `get_rc_file()` - get shell RC file path
- [x] Implement `get_completion_dir()` - get completion directory
- [x] Implement `install_completion()` - install for shell
- [x] Implement `print_completion_script()` - print script
- [x] Add `prompt_shell_completion()` to config_cmd.py
- [x] Integrate completion install into config --init
- [x] Create `tests/test_completion.py`
- [x] Update test_config_cmd.py for new prompt

**Files:** `completion.py`, `config_cmd.py`, `test_completion.py`, `test_config_cmd.py`

---

## Phase 5f: Documentation

- [x] Update table of contents in USER_MANUAL.md
- [x] Add `skilz config` command section
- [x] Add Configuration section (Config File, Env Vars, Override Hierarchy)
- [x] Add Shell Completion section
- [x] Add Global Flags section
- [x] Add Scripting & Automation section
- [x] Create SDD artifacts (specify.md, plan.md, tasks.md)

**Files:** `docs/USER_MANUAL.md`, `.speckit/features/05-configuration/*`

---

## Test Coverage Summary

| Test File | Tests Added |
|-----------|-------------|
| test_cli.py | 5 |
| test_remove_cmd.py | 2 |
| test_config.py | 22 |
| test_agents.py | 6 |
| test_config_cmd.py | 20 |
| test_completion.py | 21 |
| **Total** | **76** |

Final test count: **239 tests passing** (up from 165)
