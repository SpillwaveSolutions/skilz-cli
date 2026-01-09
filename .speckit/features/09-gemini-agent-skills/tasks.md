# Feature 09: Gemini CLI Native Agent Skills - Tasks

## Phase 9a: Agent Registry Update

### T1: Update Gemini CLI AgentConfig
- [ ] Modify `src/skilz/agent_registry.py:150-159`
  - Change `home_dir` from `None` to `Path.home() / ".gemini" / "skills"`
  - Change `project_dir` from `Path(".skilz") / "skills"` to `Path(".gemini") / "skills"`
  - Change `supports_home` from `False` to `True`
  - Change `native_skill_support` from `"none"` to `"all"`
  - Add `invocation="/skills or activate_skill tool"`
- **DoD:** Gemini config matches Claude/OpenCode structure for native support

**Files Changed:**
- `src/skilz/agent_registry.py:150-159`

**Test Coverage:**
- `tests/test_agent_registry.py:test_gemini_config_native_support` (new)
- `tests/test_agent_registry.py:test_gemini_supports_home` (new)

---

## Phase 9b: Skill Name Validation

### T2: Add Skill Name Validation Functions
- [ ] Add `SkillNameValidation` dataclass to `src/skilz/agent_registry.py`
  - Fields: `is_valid`, `normalized_name`, `errors`, `suggested_name`
- [ ] Implement `validate_skill_name(name: str) -> SkillNameValidation`
  - NFKC Unicode normalization
  - Regex pattern: `^[a-z][a-z0-9]*(-[a-z0-9]+)*$`
  - Max 64 character check
  - Return validation result with suggestions
- [ ] Implement `_suggest_valid_name(name: str) -> str` helper
  - Convert uppercase → lowercase
  - Replace spaces/underscores → hyphens
  - Remove invalid characters
  - Remove consecutive hyphens
  - Ensure starts with letter
- [ ] Implement `check_skill_directory_name(skill_dir: Path, expected_name: str) -> tuple[bool, str | None]`
  - Compare directory name with skill name
  - Return (matches, suggested_path)
- [ ] Implement `rename_skill_directory(skill_dir: Path, new_name: str) -> Path`
  - Rename directory to match skill name
  - Raise FileExistsError if target exists
- **DoD:** All validation functions working with comprehensive error messages

**Files Changed:**
- `src/skilz/agent_registry.py:280-433` (add after existing functions)

**Test Coverage:**
- `tests/test_agent_registry.py:test_validate_skill_name_valid`
- `tests/test_agent_registry.py:test_validate_skill_name_invalid_uppercase`
- `tests/test_agent_registry.py:test_validate_skill_name_invalid_underscores`
- `tests/test_agent_registry.py:test_validate_skill_name_invalid_special_chars`
- `tests/test_agent_registry.py:test_validate_skill_name_leading_hyphen`
- `tests/test_agent_registry.py:test_validate_skill_name_consecutive_hyphens`
- `tests/test_agent_registry.py:test_validate_skill_name_max_length`
- `tests/test_agent_registry.py:test_validate_skill_name_unicode_normalization`
- `tests/test_agent_registry.py:test_check_skill_directory_name_match`
- `tests/test_agent_registry.py:test_check_skill_directory_name_mismatch`
- `tests/test_agent_registry.py:test_rename_skill_directory_success`
- `tests/test_agent_registry.py:test_rename_skill_directory_exists_error`

---

## Phase 9c: Detection Enhancement

### T3: Update Agent Detection Logic
- [ ] Modify `src/skilz/agents.py:detect_agent()` function
  - After Claude checks, add Gemini checks:
    - Check for `.gemini/` in project directory
    - Check for `~/.gemini/` in user home
    - Return "gemini" if found
  - Place before OpenCode check (priority order)
- **DoD:** Gemini auto-detected when `.gemini/` directory exists

**Files Changed:**
- `src/skilz/agents.py:127-188` (update detect_agent function)

**Test Coverage:**
- `tests/test_agents.py:test_detect_agent_gemini_project_dir`
- `tests/test_agents.py:test_detect_agent_gemini_user_dir`
- `tests/test_agents.py:test_detect_agent_gemini_priority_over_opencode`
- `tests/test_agents.py:test_detect_agent_claude_priority_over_gemini`
- `tests/test_agents.py:test_get_skills_dir_gemini_project`
- `tests/test_agents.py:test_get_skills_dir_gemini_user`

---

## Phase 9d: Installation Logic Updates

### T4: Add Skill Name Validation to Installation Flow
- [ ] Modify `src/skilz/git_install.py:install_from_git()`
  - After parsing SKILL.md frontmatter, validate skill name
  - Only for agents with `native_skill_support != "none"`
  - Show error with suggestion if invalid:
    ```
    Error: Skill name 'My_Cool_Skill' is invalid for Gemini CLI.
    
    Skill names must be lowercase with hyphens only.
    Suggested name: my-cool-skill
    
    Update SKILL.md frontmatter:
    ---
    name: my-cool-skill
    description: ...
    ---
    ```
- [ ] Check directory name matches skill name
  - Show warning if mismatch
  - Suggest rename command
- **DoD:** Invalid skill names caught at install time with helpful errors

**Files Changed:**
- `src/skilz/git_install.py:~200-280` (add validation step)

**Test Coverage:**
- `tests/test_git_install.py:test_validate_skill_name_gemini_native`
- `tests/test_git_install.py:test_invalid_skill_name_error_message`
- `tests/test_git_install.py:test_skill_name_validation_skipped_non_native`
- `tests/test_git_install.py:test_directory_name_mismatch_warning`

### T5: Update Config Sync Logic for Native Gemini
- [ ] Modify `src/skilz/commands/install_cmd.py`
  - For Gemini with `native_skill_support="all"`, set `skip_config_sync=True` by default
  - If `--force-config` flag provided, override to use legacy paths:
    - Install to `.skilz/skills/` instead of `.gemini/skills/`
    - Enable GEMINI.md sync
- [ ] Update `src/skilz/config_sync.py` (if changes needed)
  - Ensure GEMINI.md sync can still be forced for backward compatibility
- **DoD:** Native Gemini installs skip config sync; --force-config restores old behavior

**Files Changed:**
- `src/skilz/commands/install_cmd.py:~70-100`
- `src/skilz/config_sync.py` (verify, may not need changes)

**Test Coverage:**
- `tests/test_install_cmd.py:test_install_gemini_native_skip_config`
- `tests/test_install_cmd.py:test_install_gemini_force_config_legacy_path`
- `tests/test_install_cmd.py:test_install_gemini_force_config_syncs_md`

### T6: Update Installer Module
- [ ] Review `src/skilz/installer.py` for any Gemini-specific logic
  - Ensure native path resolution works correctly
  - Verify manifest generation includes correct paths
- **DoD:** installer.py handles Gemini native paths correctly

**Files Changed:**
- `src/skilz/installer.py` (review and update if needed)

**Test Coverage:**
- `tests/test_installer.py:test_install_gemini_native_path`
- `tests/test_installer.py:test_install_gemini_user_level`

---

## Phase 9e: Testing

### T7: Add Unit Tests for Validation
- [ ] Create comprehensive unit tests in `tests/test_agent_registry.py`
  - Cover all validation edge cases (see T2 test list)
  - Test Unicode normalization (e.g., full-width characters)
  - Test max length boundary conditions
- [ ] Update `tests/conftest.py` if new fixtures needed
- **DoD:** 100% coverage of validation code paths

**Files Changed:**
- `tests/test_agent_registry.py` (add ~150 LOC of tests)

### T8: Add Integration Tests
- [ ] Create `tests/test_gemini_integration.py`
  - `test_install_skill_to_gemini_native_project`
  - `test_install_skill_to_gemini_native_user`
  - `test_gemini_auto_detection_project`
  - `test_gemini_auto_detection_user`
  - `test_gemini_backward_compat_force_config`
  - `test_gemini_invalid_skill_name_error`
  - `test_gemini_list_user_and_project_skills`
- [ ] Use temporary directories for test isolation
- [ ] Mock git operations where appropriate
- **DoD:** All integration scenarios pass, 80%+ overall coverage maintained

**Files Changed:**
- `tests/test_gemini_integration.py` (new file, ~200 LOC)

### T9: Update Existing Tests
- [ ] Review all existing tests for Gemini assumptions
  - `tests/test_agents.py` - Add Gemini detection tests
  - `tests/test_list_cmd.py` - Test listing Gemini skills
  - `tests/test_update_cmd.py` - Test updating Gemini skills
  - `tests/test_remove_cmd.py` - Test removing Gemini skills
- [ ] Fix any tests broken by Gemini config changes
- **DoD:** All existing tests pass with new Gemini config

**Files Changed:**
- Various test files (update as needed)

---

## Phase 9f: Documentation

### T10: Create Gemini Migration Guide
- [ ] Create `docs/GEMINI_MIGRATION.md`
  - Explain native skills vs legacy mode
  - How to enable `experimental.skills` in Gemini CLI
  - Step-by-step migration from `.skilz/skills/` to `.gemini/skills/`
  - Troubleshooting section
  - When to use `--force-config`
- **DoD:** Clear guide for users upgrading to native Gemini support

**Files Created:**
- `docs/GEMINI_MIGRATION.md` (new file, ~150 LOC)

### T11: Update README.md
- [ ] Update agent support table
  - Show Gemini with user-level support
  - Update "Native Skill Support" column to "all"
- [ ] Add Gemini CLI examples in Quick Start section
  ```bash
  # Install for Gemini CLI (native support)
  skilz install anthropics_skills/theme-factory --agent gemini
  
  # User-level install for Gemini
  skilz install anthropics_skills/theme-factory --agent gemini --user
  ```
- [ ] Update "How It Works" section to mention Gemini native discovery
- **DoD:** README reflects Gemini native support

**Files Changed:**
- `README.md:220-242` (agent table)
- `README.md:62-93` (quick start examples)

### T12: Update USER_MANUAL.md
- [ ] Add Gemini CLI section under "Supported Agents"
  - Native skills directory: `.gemini/skills/`
  - User-level: `~/.gemini/skills/`
  - Invocation: `/skills` slash command or `activate_skill` tool
  - Link to GEMINI_MIGRATION.md
- [ ] Add Gemini examples to each command section
- [ ] Add troubleshooting section for Gemini
- **DoD:** USER_MANUAL.md has complete Gemini documentation

**Files Changed:**
- `docs/USER_MANUAL.md` (add Gemini sections)

### T13: Update COMPREHENSIVE_USER_GUIDE.md
- [ ] Add Gemini CLI to agent-specific instructions
  - Discovery tiers explanation
  - Progressive disclosure concept
  - Native vs legacy mode comparison
- [ ] Update workflow diagrams if needed
- **DoD:** COMPREHENSIVE_USER_GUIDE.md includes Gemini workflows

**Files Changed:**
- `docs/COMPREHENSIVE_USER_GUIDE.md` (add Gemini section)

### T14: Update CHANGELOG.md
- [ ] Add entry for version 1.7.0 (or next version):
  ```markdown
  ## [1.7.0] - 2025-01-XX
  
  ### Added
  - Native support for Gemini CLI Agent Skills (experimental.skills)
  - User-level installation for Gemini CLI (`~/.gemini/skills/`)
  - Skill name validation for native agents (agentskills.io spec)
  - `docs/GEMINI_MIGRATION.md` - Migration guide for Gemini users
  
  ### Changed
  - Gemini CLI now installs to `.gemini/skills/` by default (native)
  - Agent detection now checks for `.gemini/` directories
  - Config sync skipped for native Gemini installs
  
  ### Deprecated
  - Legacy Gemini mode (`.skilz/skills/` + GEMINI.md) still available via --force-config
  ```
- **DoD:** CHANGELOG.md documents all changes

**Files Changed:**
- `CHANGELOG.md` (add new version section)

---

## Task Dependencies

```
T1 (Registry Update)
│
├─► T2 (Validation Functions)
│   │
│   └─► T4 (Validation in Install Flow)
│       │
│       ├─► T7 (Unit Tests - Validation)
│       └─► T8 (Integration Tests)
│
└─► T3 (Detection Logic)
    │
    └─► T5 (Config Sync Update)
        │
        └─► T6 (Installer Module Review)
            │
            └─► T9 (Update Existing Tests)
                │
                └─► T10-T14 (Documentation)
```

## Estimated Complexity

| Task | Complexity | LOC | Days |
|------|------------|-----|------|
| T1: Registry Update | Low | 10 | 0.25 |
| T2: Validation Functions | Medium | 120 | 1 |
| T3: Detection Logic | Low | 15 | 0.5 |
| T4: Validation in Install | Medium | 40 | 0.75 |
| T5: Config Sync Update | Low | 20 | 0.5 |
| T6: Installer Review | Low | 10 | 0.25 |
| T7: Unit Tests - Validation | Medium | 150 | 1 |
| T8: Integration Tests | High | 200 | 1.5 |
| T9: Update Existing Tests | Medium | 50 | 0.5 |
| T10: Migration Guide | Medium | 150 | 0.75 |
| T11: Update README | Low | 30 | 0.25 |
| T12: Update USER_MANUAL | Low | 80 | 0.5 |
| T13: Update GUIDE | Low | 60 | 0.5 |
| T14: Update CHANGELOG | Low | 20 | 0.25 |
| **Total** | | **955** | **8.5** |

## Completion Checklist

- [ ] **Code Complete:**
  - [ ] All 14 tasks implemented
  - [ ] Code reviewed and approved
  - [ ] No linting or type errors

- [ ] **Testing Complete:**
  - [ ] All new unit tests passing
  - [ ] All integration tests passing
  - [ ] Overall coverage ≥80%
  - [ ] Manual testing on real Gemini CLI project

- [ ] **Documentation Complete:**
  - [ ] README.md updated
  - [ ] USER_MANUAL.md updated
  - [ ] COMPREHENSIVE_USER_GUIDE.md updated
  - [ ] GEMINI_MIGRATION.md created
  - [ ] CHANGELOG.md updated

- [ ] **Verification:**
  - [ ] Can install skill to `.gemini/skills/` (native)
  - [ ] Can install skill to `~/.gemini/skills/` (user-level)
  - [ ] Gemini CLI auto-detects installed skills
  - [ ] Backward compat works with --force-config
  - [ ] Invalid skill names show helpful errors

## Success Metrics

Feature is complete when:
1. `skilz install <skill> --agent gemini` installs to `.gemini/skills/` ✓
2. `skilz install <skill> --agent gemini --user` installs to `~/.gemini/skills/` ✓
3. Gemini CLI's `/skills list` shows Skilz-installed skills ✓
4. Auto-detection works when `.gemini/` directory exists ✓
5. Invalid skill names are caught with helpful messages ✓
6. Tests pass with ≥80% coverage ✓
7. Migration guide published ✓
8. No regressions in existing agent support ✓
