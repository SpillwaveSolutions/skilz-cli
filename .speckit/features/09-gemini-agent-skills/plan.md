# Feature 09: Gemini CLI Native Agent Skills - Technical Plan

## Technology Stack

| Component | Choice | Rationale |
|-----------|--------|-----------|
| Agent Registry | Python dataclasses | Already used, immutable configs |
| Validation | Regex + unicodedata | Lightweight, stdlib-only for name validation |
| Detection | pathlib | Consistent with existing agent detection |
| Config Files | YAML (manifest) | Maintains consistency with existing Skilz |

## Architecture

### Component Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                     Agent Registry Layer                         │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │         agent_registry.py (UPDATED)                         │ │
│  │                                                             │ │
│  │  AgentConfig(gemini):                                      │ │
│  │    - home_dir: ~/.gemini/skills (NEW)                      │ │
│  │    - project_dir: .gemini/skills (CHANGED)                 │ │
│  │    - supports_home: True (CHANGED)                         │ │
│  │    - native_skill_support: "all" (CHANGED)                 │ │
│  │    - invocation: "/skills or activate_skill" (NEW)         │ │
│  └────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────────┐
│                   Detection Layer                                │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │              agents.py (UPDATED)                            │ │
│  │                                                             │ │
│  │  detect_agent():                                           │ │
│  │    1. Check config default                                 │ │
│  │    2. Check .claude/                                       │ │
│  │    3. Check ~/.claude/                                     │ │
│  │    4. Check .gemini/ (NEW)                                 │ │
│  │    5. Check ~/.gemini/ (NEW)                               │ │
│  │    6. Check ~/.config/opencode/                            │ │
│  │    7. Other agents                                         │ │
│  └────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────────┐
│                 Validation Layer (NEW)                           │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │         agent_registry.py (skill validation)                │ │
│  │                                                             │ │
│  │  validate_skill_name(name):                                │ │
│  │    - NFKC Unicode normalization                            │ │
│  │    - Regex: ^[a-z][a-z0-9]*(-[a-z0-9]+)*$                  │ │
│  │    - Max 64 chars                                          │ │
│  │    - Returns: SkillNameValidation                          │ │
│  │                                                             │ │
│  │  check_skill_directory_name(dir, expected_name):           │ │
│  │    - Compare directory name with SKILL.md name             │ │
│  │    - Suggest rename if mismatch                            │ │
│  └────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────────┐
│                  Installation Layer                              │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │          git_install.py / installer.py                      │ │
│  │                                                             │ │
│  │  1. Clone/checkout skill from Git                          │ │
│  │  2. Parse SKILL.md frontmatter                             │ │
│  │  3. Validate skill name (Gemini only)                      │ │
│  │  4. Check directory name matches (Gemini only)             │ │
│  │  5. Copy to .gemini/skills/ or ~/.gemini/skills/           │ │
│  │  6. Write .skilz-manifest.yaml                             │ │
│  │  7. Skip GEMINI.md sync (unless --force-config)            │ │
│  └────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

### Data Flow: Native Gemini Installation

```
1. User runs: skilz install anthropics_skills/theme-factory --agent gemini

2. install_cmd.py:
   - Detects agent="gemini"
   - Checks AgentConfig(gemini).native_skill_support == "all"
   - Sets skip_config_sync=True (no GEMINI.md sync)

3. installer.py or git_install.py:
   - Clones repository to cache
   - Finds SKILL.md at skill_path
   - Parses frontmatter:
       name: "theme-factory"
       description: "..."

4. validation (NEW for Gemini):
   - validate_skill_name("theme-factory")
     → SkillNameValidation(is_valid=True, normalized="theme-factory")
   - check_skill_directory_name(skill_dir, "theme-factory")
     → matches=True

5. copy to .gemini/skills/:
   - Target: .gemini/skills/theme-factory/
   - Copy all files (SKILL.md, scripts/, references/, assets/)
   - Write .skilz-manifest.yaml

6. NO GEMINI.md sync (native support)

7. User opens Gemini CLI:
   - /skills list → shows "theme-factory" (discovered automatically)
   - Can use /skills enable theme-factory, /skills disable theme-factory
```

### Data Flow: Backward Compatibility (--force-config)

```
1. User runs: skilz install <skill> --agent gemini --force-config

2. install_cmd.py:
   - Detects agent="gemini"
   - --force-config flag overrides native_skill_support
   - Sets skip_config_sync=False

3. installer.py:
   - Installs to .skilz/skills/ (old path)
   - Writes GEMINI.md entry with skilz read command

4. User must manually load skill via skilz read
```

## Key Design Decisions

### D1: User-Level Support for Gemini
**Decision:** Enable `supports_home=True` for Gemini CLI

**Rationale:** 
- Gemini CLI's spec explicitly supports `~/.gemini/skills/` as "User Skills" tier
- Precedence model (project > user > extension) matches other agents (claude, opencode)
- Users expect to share skills across multiple projects

**Code Change:**
```python
# agent_registry.py:150-159
"gemini": AgentConfig(
    home_dir=Path.home() / ".gemini" / "skills",  # NEW
    supports_home=True,                            # CHANGED
)
```

### D2: Native Support Level
**Decision:** Set `native_skill_support="all"` for Gemini CLI

**Rationale:**
- Gemini CLI reads `.gemini/skills/` directly via `activate_skill` tool
- Skills are discovered by name/description without config file parsing
- Same as Claude Code and OpenCode native support

**Code Change:**
```python
# agent_registry.py:158
native_skill_support="all",  # CHANGED from "none"
```

### D3: Skill Name Validation
**Decision:** Validate skill names only for Gemini (and agents with native support)

**Rationale:**
- Claude Code and Gemini CLI fail if skill names don't match agentskills.io spec
- Better to catch errors at install time than runtime
- Non-native agents (aider, cursor) don't care about name format

**Implementation:**
- Add validation functions to `agent_registry.py` (reusable)
- Call during installation for agents with `native_skill_support != "none"`
- Show helpful error with suggested fix

### D4: Detection Priority
**Decision:** Check Gemini after Claude but before OpenCode

**Rationale:**
- Claude Code is most common, check first
- Gemini CLI is newer than OpenCode
- Avoids false positives from `.skilz/` directory (universal fallback)

**Code Change:**
```python
# agents.py:detect_agent()
# Order: Claude → Gemini → OpenCode → Others
if (Path.home() / ".claude").exists():
    return "claude"
if (project / ".gemini").exists() or (Path.home() / ".gemini").exists():
    return "gemini"
if (Path.home() / ".config" / "opencode").exists():
    return "opencode"
```

### D5: Backward Compatibility via Flag
**Decision:** Keep `.skilz/skills/` support with `--force-config` flag

**Rationale:**
- Users on older Gemini CLI (without `experimental.skills`) still need to work
- Gradual migration path for existing users
- Same pattern as `--force-config` for other native agents

**Behavior:**
- Default (no flag): use `.gemini/skills/` (native)
- With `--force-config`: use `.skilz/skills/` + GEMINI.md sync (legacy)

### D6: Skip Directory Name Mismatch for Non-Gemini
**Decision:** Only validate directory name for agents with native support

**Rationale:**
- Non-native agents don't care about directory names
- Avoids breaking existing installs where dir name != skill name
- Native agents (Claude, Gemini, OpenCode) require name matching for discovery

## Error Handling Strategy

| Error | Agent | Exit Code | Message |
|-------|-------|-----------|---------|
| Invalid skill name | Gemini (native) | 1 | "Skill name '<name>' is invalid. Must be lowercase, letters/digits/hyphens only.\nSuggested name: '<fixed>'" |
| Directory name mismatch | Gemini (native) | 1 | "Skill directory '<dir>' doesn't match skill name '<name>'.\nConsider renaming to '<suggested>'" |
| Native skills not enabled | Gemini | 1 | "Gemini CLI native skills not detected. Enable 'experimental.skills' or use --force-config" |
| No home support | Gemini (old) | 1 | "Gemini CLI does not support user-level installation. Use --project flag." (only if supports_home=False) |

## Testing Strategy

### Unit Tests (New)

#### test_agent_registry.py
- `test_gemini_config_updated` - Verify home_dir, supports_home, native_skill_support
- `test_validate_skill_name_valid` - Valid names pass
- `test_validate_skill_name_invalid_uppercase` - Suggest lowercase
- `test_validate_skill_name_invalid_underscores` - Suggest hyphens
- `test_validate_skill_name_invalid_leading_hyphen` - Suggest fix
- `test_validate_skill_name_max_length` - Truncate to 64 chars
- `test_check_skill_directory_name_match` - Dir matches name
- `test_check_skill_directory_name_mismatch` - Suggest rename
- `test_rename_skill_directory` - Actually rename directory

#### test_agents.py
- `test_detect_agent_gemini_project` - Detect `.gemini/`
- `test_detect_agent_gemini_user` - Detect `~/.gemini/`
- `test_detect_agent_gemini_priority` - Gemini before OpenCode
- `test_get_skills_dir_gemini_project` - Resolve `.gemini/skills/`
- `test_get_skills_dir_gemini_user` - Resolve `~/.gemini/skills/`

#### test_install_cmd.py (Updated)
- `test_install_gemini_native_skip_config` - No GEMINI.md sync by default
- `test_install_gemini_force_config` - GEMINI.md sync with --force-config
- `test_install_gemini_user_level` - Install to `~/.gemini/skills/`

#### test_git_install.py (Updated)
- `test_validate_skill_name_during_install` - Validation runs for Gemini
- `test_invalid_skill_name_error` - Helpful error message
- `test_skip_validation_non_native` - No validation for aider, cursor

### Integration Tests

#### test_gemini_end_to_end.py (NEW)
```python
def test_install_skill_to_gemini_native():
    """Install skill to .gemini/skills/ with native support."""
    # Given: Gemini project with .gemini/ directory
    # When: skilz install <skill> --agent gemini
    # Then: Skill in .gemini/skills/, no GEMINI.md sync

def test_install_skill_to_gemini_user_level():
    """Install skill to ~/.gemini/skills/ for user-level."""
    # Given: User wants personal skill
    # When: skilz install <skill> --agent gemini --user
    # Then: Skill in ~/.gemini/skills/

def test_gemini_auto_detection():
    """Auto-detect Gemini from .gemini/ directory."""
    # Given: Project with .gemini/ directory
    # When: skilz install <skill> (no --agent flag)
    # Then: Detects agent=gemini, installs to .gemini/skills/

def test_backward_compat_force_config():
    """Backward compat with --force-config."""
    # Given: Older Gemini setup
    # When: skilz install <skill> --agent gemini --force-config
    # Then: Installs to .skilz/skills/, syncs GEMINI.md
```

## Implementation Phases

### Phase 9a: Agent Registry Update
- [x] Update `agent_registry.py` Gemini CLI config
  - home_dir = `~/.gemini/skills/`
  - project_dir = `.gemini/skills/`
  - supports_home = True
  - native_skill_support = "all"
  - invocation = "/skills or activate_skill tool"

### Phase 9b: Skill Name Validation
- [ ] Add `validate_skill_name()` to `agent_registry.py`
- [ ] Add `check_skill_directory_name()` to `agent_registry.py`
- [ ] Add `rename_skill_directory()` to `agent_registry.py`
- [ ] Add `SkillNameValidation` dataclass

### Phase 9c: Detection Enhancement
- [ ] Update `detect_agent()` in `agents.py`
  - Check `.gemini/` in project
  - Check `~/.gemini/` in user home
  - Insert before OpenCode check

### Phase 9d: Installation Logic
- [ ] Update `git_install.py` to validate skill names for native agents
- [ ] Update `installer.py` to skip GEMINI.md sync for native Gemini
- [ ] Handle `--force-config` override for backward compatibility

### Phase 9e: Testing
- [ ] Add unit tests for validation functions
- [ ] Add unit tests for detection
- [ ] Add integration tests for end-to-end flows
- [ ] Test backward compatibility with --force-config

### Phase 9f: Documentation
- [ ] Update README.md with Gemini native support
- [ ] Update USER_MANUAL.md with Gemini examples
- [ ] Update COMPREHENSIVE_USER_GUIDE.md
- [ ] Create GEMINI_MIGRATION.md guide
- [ ] Update agent table in README (native support column)

## Migration Path for Existing Users

### For Users on Older Gemini CLI (No Native Skills)

```bash
# Continue using legacy mode
skilz install <skill> --agent gemini --force-config
```

### For Users Upgrading to Native Gemini CLI

1. **Enable experimental.skills in Gemini CLI:**
   ```bash
   # In Gemini CLI /settings UI, search for "Skills" and toggle "experimental.skills"
   ```

2. **Migrate existing skills:**
   ```bash
   # Option 1: Reinstall skills (recommended)
   skilz uninstall <skill> --agent gemini
   skilz install <skill> --agent gemini  # Now goes to .gemini/skills/

   # Option 2: Manual move (advanced)
   mv .skilz/skills/theme-factory .gemini/skills/
   # Remove GEMINI.md entries manually
   ```

3. **Verify:**
   ```bash
   # In Gemini CLI
   /skills list  # Should show migrated skills
   ```

## Rollback Plan

If native support causes issues:

1. **Revert agent config:**
   ```python
   # In ~/.config/skilz/config.json (user override)
   {
     "agents": {
       "gemini": {
         "display_name": "Gemini CLI",
         "home_dir": null,
         "project_dir": ".skilz/skills",
         "config_files": ["GEMINI.md"],
         "supports_home": false,
         "default_mode": "copy",
         "native_skill_support": "none"
       }
     }
   }
   ```

2. **Use --force-config flag:**
   ```bash
   skilz install <skill> --agent gemini --force-config
   ```

## Performance Considerations

- Skill name validation adds ~1ms per install (regex + Unicode normalization)
- Directory checks add ~5ms per install (stat calls)
- Overall install time impact: <1% (dominated by git clone)

## Security Considerations

- Validation prevents directory traversal attacks (rejects `../` in names)
- NFKC normalization prevents Unicode homograph attacks
- No new file permissions or execution beyond existing installer

## Compatibility Matrix

| Gemini CLI Version | experimental.skills | Skilz Behavior |
|--------------------|-------------------|----------------|
| <2.0 (hypothetical) | Not available | Install to `.skilz/skills/` + GEMINI.md |
| ≥2.0 without flag | Disabled | Install to `.skilz/skills/` + GEMINI.md (use --force-config) |
| ≥2.0 with flag | Enabled | Install to `.gemini/skills/` (native) |

## Dependencies

No new external dependencies. All new code uses:
- `pathlib` (stdlib)
- `re` (stdlib)
- `unicodedata` (stdlib)
- `dataclasses` (stdlib)

## Estimated Complexity

| Phase | Complexity | LOC | Days |
|-------|------------|-----|------|
| 9a: Registry Update | Low | 10 | 0.25 |
| 9b: Validation | Medium | 120 | 1 |
| 9c: Detection | Low | 15 | 0.5 |
| 9d: Installation | Medium | 50 | 1 |
| 9e: Testing | High | 300 | 2 |
| 9f: Documentation | Medium | 200 | 1 |
| **Total** | | **695** | **5.75** |
