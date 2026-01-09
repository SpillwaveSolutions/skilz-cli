# Feature Specification: Universal Agent Project-Level Support

**Feature ID:** SKILZ-50  
**Status:** Draft  
**Created:** 2026-01-08  
**Updated:** 2026-01-08  

---

## Overview

Add project-level installation support for the "universal" agent with optional custom config file targeting. This enables legacy Gemini CLI workflows (when `experimental.skills` is disabled) and provides a fallback installation method for any agent.

---

## Problem Statement

### Current Limitations

1. **Universal agent only supports user-level installs:**
   - `skilz install skill --agent universal` → installs to `~/.skilz/skills/`
   - No project-level option exists

2. **No way to target legacy Gemini installations:**
   - Gemini CLI without `experimental.skills` plugin reads from `GEMINI.md`
   - Native Gemini support (`.gemini/skills/`) requires plugin enabled
   - Users without plugin access are stuck

3. **No way to override config file target:**
   - Config sync always writes to agent's default config file
   - Can't redirect to custom file for special cases

### User Pain Points

**Scenario 1: Corporate Gemini User**
```bash
# User's company hasn't enabled experimental.skills plugin yet
gemini --version  # experimental.skills: disabled

# User wants to install skills but native location won't work
skilz install pdf-reader --agent gemini --project
# ❌ Installs to .gemini/skills/ but Gemini can't see it (plugin disabled)
```

**Scenario 2: Multi-Agent Project**
```bash
# User wants skills available to ALL agents in one location
# Currently must install multiple times:
skilz install pdf --agent claude --project    # → .claude/skills/
skilz install pdf --agent gemini --project    # → .gemini/skills/
skilz install pdf --agent codex --project     # → .codex/skills/
# 😢 Three copies of the same skill
```

---

## Proposed Solution

### Feature 1: Universal Agent Project-Level Support

Enable `--project` flag for universal agent with standard behavior:

```bash
skilz install my-skill --agent universal --project
```

**Behavior:**
- Installs to `./skilz/skills/my-skill/` (non-native location)
- Updates `AGENTS.md` with skill reference
- Works for any agent that reads `AGENTS.md` (Codex, legacy workflows)

**File Structure:**
```
project/
├── skilz/
│   └── skills/
│       └── my-skill/
│           ├── SKILL.md
│           └── .skilz-manifest.json
└── AGENTS.md   ← Skill reference added here
```

### Feature 2: Custom Config File Target

Add `--config` flag to override default config file:

```bash
skilz install my-skill --agent universal --project --config GEMINI.md
```

**Behavior:**
- Still installs to `./skilz/skills/my-skill/`
- Updates `GEMINI.md` instead of `AGENTS.md`
- Enables legacy Gemini support

**Use Cases:**
1. **Legacy Gemini:** Corporate users without `experimental.skills` plugin
2. **Testing:** Test config file generation without affecting native installations
3. **Multi-agent:** Share one skill location, multiple config file references

---

## User Stories

### US-1: Legacy Gemini Installation

**As a** corporate Gemini CLI user without the `experimental.skills` plugin  
**I want to** install skills that Gemini can discover  
**So that** I can use Skilz without waiting for admin approval

**Acceptance Criteria:**
```bash
# Install skill for legacy Gemini
skilz install pdf-reader --agent universal --project --config GEMINI.md

# Verify installation
ls ./skilz/skills/pdf-reader/SKILL.md  # ✅ Exists
cat GEMINI.md | grep pdf-reader         # ✅ Referenced

# Gemini can now read it
gemini  # Skill shows up in /skills command
```

### US-2: Universal Project Installation

**As a** developer working on a multi-agent project  
**I want to** install skills once in a shared location  
**So that** multiple agents can reference the same files

**Acceptance Criteria:**
```bash
# Install skill universally at project level
skilz install web-scraper --agent universal --project

# Verify installation
ls ./skilz/skills/web-scraper/SKILL.md  # ✅ Exists
cat AGENTS.md | grep web-scraper         # ✅ Referenced

# All agents using AGENTS.md can discover it
```

### US-3: Config File Override

**As a** power user testing skill installations
**I want to** control which config file gets updated
**So that** I can test without breaking my main setup

**Acceptance Criteria:**
```bash
# Test installation with custom config (registry install)
skilz install test-skill --agent universal --project --config TEST.md

# Test git installation with custom config
skilz install https://github.com/owner/repo --agent universal --project --config TEST.md

# Verify only TEST.md was modified
cat TEST.md | grep test-skill   # ✅ Referenced
cat AGENTS.md | grep test-skill # ❌ Not modified
```

---

## Technical Design

### Changes Required

#### 1. Update Universal Agent Config

**File:** `src/skilz/agent_registry.py`

**Current:**
```python
"universal": AgentConfig(
    name="universal",
    display_name="Universal (Skilz)",
    home_dir=Path.home() / ".skilz" / "skills",
    project_dir=Path(".skilz") / "skills",
    config_files=(),  # ← Empty!
    supports_home=True,
    default_mode="copy",
    native_skill_support="none",
),
```

**Proposed:**
```python
"universal": AgentConfig(
    name="universal",
    display_name="Universal (Skilz)",
    home_dir=Path.home() / ".skilz" / "skills",
    project_dir=Path(".skilz") / "skills",
    config_files=("AGENTS.md",),  # ← Add default config
    supports_home=True,
    default_mode="copy",
    native_skill_support="none",
),
```

#### 2. Add --config Flag to CLI

**File:** `src/skilz/cli.py`

```python
# Add to install command parser
parser_install.add_argument(
    "--config",
    metavar="FILE",
    help="Config file to update (overrides agent default). Example: --config GEMINI.md"
)
```

#### 3. Update Installer Logic

**File:** `src/skilz/installer.py`

```python
def install_local_skill(
    source_path: Path,
    agent: AgentType | None = None,
    project_level: bool = False,
    verbose: bool = False,
    mode: InstallMode | None = None,
    git_url: str | None = None,
    git_sha: str | None = None,
    skill_name: str | None = None,
    force_config: bool = False,
    config_file: str | None = None,  # ← NEW parameter
) -> None:
    # ... existing logic ...
    
    # Step 5: Sync skill reference to config files
    if project_level and should_sync:
        # Determine config files to update
        if config_file:
            # Use user-specified config file
            config_files = (config_file,)
        else:
            # Use agent's default config files
            config_files = agent_config.config_files
        
        sync_results = sync_skill_to_configs(
            skill=skill_ref,
            project_dir=project_dir,
            target_files=config_files,  # ← Use determined files
        )
```

#### 4. Update Config Sync Logic

**File:** `src/skilz/config_sync.py`

```python
def sync_skill_to_configs(
    skill: SkillReference,
    project_dir: Path,
    target_files: tuple[str, ...] | None = None,  # ← NEW: override files
) -> list[ConfigSyncResult]:
    """Sync skill reference to agent config files.
    
    Args:
        skill: Skill information to add to config files.
        project_dir: Project root directory.
        target_files: Optional list of config files to update.
                     If None, uses all known agent config files.
    """
    if target_files:
        # Use provided files only
        config_files = target_files
    else:
        # Auto-detect all agent config files
        config_files = ("CLAUDE.md", "AGENTS.md", "GEMINI.md", "OPENCODE.md")
    
    # ... rest of logic
```

---

## Implementation Plan

### Phase 10a: Universal Agent Config Update
- [ ] Update `universal` AgentConfig to include `config_files=("AGENTS.md",)`
- [ ] Add tests for universal agent config
- **Files:** `src/skilz/agent_registry.py`, `tests/test_agent_registry.py`
- **Effort:** 1 hour

### Phase 10b: CLI Flag Addition
- [ ] Add `--config FILE` argument to install command
- [ ] Add argument validation (file name only, no path traversal)
- [ ] Update help text
- **Files:** `src/skilz/cli.py`, `tests/test_cli.py`
- **Effort:** 2 hours

### Phase 10c: Installer Integration
- [ ] Add `config_file` parameter to `install_local_skill()`
- [ ] Add `config_file` parameter to `install_skill()`
- [ ] Pass custom config to `sync_skill_to_configs()`
- [ ] Add validation: `--config` only works with `--project`
- **Files:** `src/skilz/installer.py`, `tests/test_installer.py`
- **Effort:** 3 hours

### Phase 10d: Config Sync Enhancement
- [ ] Add `target_files` parameter to `sync_skill_to_configs()`
- [ ] Update sync logic to use custom files when provided
- [ ] Add `config_file` parameter to `install_from_git()` function
- [ ] Pass `config_file` through git install flow to local install
- [ ] Preserve backward compatibility (default behavior unchanged)
- **Files:** `src/skilz/config_sync.py`, `src/skilz/git_install.py`, `tests/test_config_sync.py`
- **Effort:** 3 hours

### Phase 10e: Integration Testing
- [ ] Test: Universal project install creates AGENTS.md
- [ ] Test: Universal + --config creates custom file
- [ ] Test: --config without --project shows error
- [ ] Test: Legacy Gemini workflow (--agent universal --config GEMINI.md)
- **Files:** `tests/test_universal_integration.py` (new)
- **Effort:** 3 hours

### Phase 10f: Documentation
- [ ] Update USER_MANUAL.md with universal project examples
- [ ] Update README.md with legacy Gemini workflow
- [ ] Create UNIVERSAL_AGENT_GUIDE.md
- [ ] Update CHANGELOG.md for version 1.7.0
- **Files:** `docs/`
- **Effort:** 2 hours

---

## Total Effort Estimate

**Total:** 13 hours (~2 days)

---

## Testing Strategy

### Unit Tests
- `test_universal_agent_config()` - Config includes AGENTS.md
- `test_config_flag_validation()` - Only works with --project
- `test_custom_config_file_sync()` - Updates specified file only

### Integration Tests
- `test_universal_project_install()` - Creates ./skilz/skills/ + AGENTS.md
- `test_universal_custom_config()` - Creates ./skilz/skills/ + custom file
- `test_legacy_gemini_workflow()` - Full legacy install flow

### Manual Testing
```bash
# Test 1: Universal project install
cd test-project/
skilz install pdf --agent universal --project
ls ./skilz/skills/pdf/  # ✅ Exists
cat AGENTS.md           # ✅ Has pdf reference

# Test 2: Custom config file
skilz install pdf --agent universal --project --config GEMINI.md
cat GEMINI.md           # ✅ Has pdf reference
cat AGENTS.md           # ❌ Not modified

# Test 3: Error handling
skilz install pdf --agent universal --config TEST.md
# ❌ Error: --config requires --project
```

---

## Success Metrics

- [ ] Universal agent supports `--project` flag
- [ ] `--config` flag allows custom config file targeting
- [ ] All 602 existing tests pass
- [ ] 8+ new tests for universal agent features
- [ ] Documentation includes legacy Gemini workflow example

---

## Future Enhancements

### Multi-Config Support
```bash
# Update multiple config files at once
skilz install pdf --agent universal --project \
  --config AGENTS.md --config GEMINI.md --config CLAUDE.md
```

### Auto-Detect Config Files
```bash
# Scan project for all *AGENTS*.md files and update them all
skilz install pdf --agent universal --project --config auto
```
