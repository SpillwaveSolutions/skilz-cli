# Feature 09: Gemini CLI Native Agent Skills Support

## Feature Summary

Update Skilz to support Gemini CLI's new native Agent Skills feature. Gemini CLI now supports the Agent Skills open standard with progressive disclosure via `activate_skill` tool, discovery tiers (project, user, extension), and SKILL.md format with YAML frontmatter.

This feature aligns Skilz with Gemini CLI's native skill capabilities, similar to how Claude Code and OpenCode already work.

## Background

Gemini CLI has added experimental native support for Agent Skills based on the Agent Skills open standard (https://github.com/agentskills). Key features:

- **Progressive Disclosure**: Skills are discovered by name/description, then activated on-demand
- **Discovery Tiers**: 
  - Project skills: `.gemini/skills/` (highest precedence)
  - User skills: `~/.gemini/skills/`
  - Extension skills: bundled with extensions (lowest precedence)
- **SKILL.md Format**: YAML frontmatter with `name` and `description`, plus Markdown instructions
- **Management**: `/skills` slash command and `gemini skills` CLI for enable/disable/reload
- **Resource Bundling**: Skills can include `scripts/`, `references/`, `assets/` subdirectories

## Target Agent

| Agent | Current Skills Directory | New Native Skills Directory | Native Support |
|-------|-------------------------|----------------------------|----------------|
| Gemini CLI | `.skilz/skills/` (non-native) | `.gemini/skills/` (native) | Experimental (requires `experimental.skills` flag) |

## User Stories

### US-1: Install Skills for Native Gemini CLI Support
**As a** developer using Gemini CLI with native skills enabled  
**I want to** run `skilz install <skill-id> --agent gemini`  
**So that** skills are installed to `.gemini/skills/` (project) or `~/.gemini/skills/` (user) and automatically discovered

**Acceptance Criteria:**
- Skills installed to `.gemini/skills/` at project level (default)
- Skills installed to `~/.gemini/skills/` with `--user` flag (NEW: user-level support)
- SKILL.md format is preserved (YAML frontmatter + Markdown body)
- Gemini CLI's `/skills list` shows installed skills
- Skills are auto-discovered without GEMINI.md entries

### US-2: Auto-Detect Gemini CLI with Native Skills
**As a** developer with native Gemini skills enabled  
**I want to** run `skilz install <skill-id>` without `--agent gemini`  
**So that** Skilz auto-detects Gemini CLI from `.gemini/` directory presence

**Acceptance Criteria:**
- Detection checks for `.gemini/` directory in project
- Detection checks for `~/.gemini/` directory at user level
- Falls back to other agent detection if not found
- Works alongside existing Claude/OpenCode detection

### US-3: Backward Compatibility with Non-Native Installs
**As a** developer using older Gemini CLI without native skills  
**I want to** continue installing skills to `.skilz/skills/` with GEMINI.md sync  
**So that** I don't break my existing workflow

**Acceptance Criteria:**
- `skilz install --agent gemini --force-config` continues to use `.skilz/skills/`
- GEMINI.md config sync still works when explicitly requested
- Clear error message if user tries native install without `experimental.skills` enabled
- Documentation explains migration path from old to new

### US-4: Skill Name Validation for Gemini
**As a** skill maintainer  
**I want to** know if my skill name is valid for Gemini CLI  
**So that** I can fix issues before installation fails

**Acceptance Criteria:**
- SKILL.md `name` field is validated against agentskills.io spec:
  - Lowercase only
  - Letters, digits, hyphens only
  - No leading/trailing hyphens
  - No consecutive hyphens
  - Max 64 characters
- Helpful error message with suggested fix if invalid
- Directory name matches `name` field (or suggests rename)

### US-5: User-Level Installation Support
**As a** developer sharing skills across multiple Gemini projects  
**I want to** install skills to `~/.gemini/skills/` once  
**So that** they're available in all my projects

**Acceptance Criteria:**
- `skilz install <skill> --agent gemini --user` installs to `~/.gemini/skills/`
- `skilz list --agent gemini --user` shows user-level skills
- User skills have lower precedence than project skills (per Gemini spec)
- Agent registry updated: `supports_home=True` for Gemini

## Functional Requirements

### FR-1: Agent Configuration Update
- Update `agent_registry.py` Gemini CLI configuration:
  ```python
  "gemini": AgentConfig(
      name="gemini",
      display_name="Gemini CLI",
      home_dir=Path.home() / ".gemini" / "skills",  # NEW: user-level support
      project_dir=Path(".gemini") / "skills",        # CHANGED: .skilz → .gemini
      config_files=("GEMINI.md",),                   # Keep for backward compat
      supports_home=True,                            # CHANGED: False → True
      default_mode="copy",
      native_skill_support="all",                    # CHANGED: "none" → "all"
      invocation="/skills or activate_skill tool",   # NEW: document invocation
  )
  ```

### FR-2: Detection Logic Enhancement
- Update `detect_agent()` in `agents.py`:
  - Check for `.gemini/` in project directory
  - Check for `~/.gemini/` in user home directory
  - Add priority before less common agents
- Order: Claude → Gemini → OpenCode → Other agents

### FR-3: SKILL.md Format Validation
- Validate SKILL.md frontmatter during installation:
  - `name` field is required
  - `description` field is required
  - `name` follows agentskills.io spec (see US-4)
- Scanner module already handles frontmatter parsing
- Add validation step in `git_install.py` before copy

### FR-4: Backward Compatibility Mode
- When `--force-config` flag is used with Gemini:
  - Install to `.skilz/skills/` (old behavior)
  - Sync to GEMINI.md
  - Set `native_skill_support="none"` temporarily
- Default behavior (no flag): use native `.gemini/skills/`

### FR-5: Migration Guide
- Add `docs/GEMINI_MIGRATION.md`:
  - How to enable `experimental.skills` in Gemini CLI
  - How to migrate from `.skilz/skills/` to `.gemini/skills/`
  - How to check if native skills are enabled (`/settings` UI)
  - Troubleshooting common issues

## Non-Functional Requirements

### NFR-1: No Breaking Changes
- Existing installs to `.skilz/skills/` continue to work
- GEMINI.md sync is opt-in (via `--force-config`)
- Clear upgrade path for users

### NFR-2: Performance
- Native skill installs should be as fast as Claude/OpenCode
- No additional overhead for skill validation

### NFR-3: Documentation
- README.md updated with Gemini native support
- USER_MANUAL.md includes Gemini examples
- COMPREHENSIVE_USER_GUIDE.md has Gemini section
- New GEMINI_MIGRATION.md for upgrading users

## Out of Scope

- Gemini CLI extension skills (bundled with extensions)
- Automatic skill enable/disable via Skilz (use `gemini skills` CLI)
- Conversion of existing `.skilz/skills/` installs to `.gemini/skills/`
- Support for Gemini CLI's `--scope` flag (project vs user) - use Skilz's `--project` flag

## Gemini CLI Skill Schema

Per Gemini CLI docs, SKILL.md format:

```markdown
---
name: skill-name
description: When to use this skill (shown to Gemini for discovery)
---

# Skill Title

Your instructions for how the agent should behave with this skill.

## Resource Structure

- `scripts/` - Executable scripts (bash, python, node)
- `references/` - Static documentation, schemas, examples
- `assets/` - Code templates, boilerplate, binaries
```

## Discovery Tiers (Gemini CLI)

1. **Project Skills** (`.gemini/skills/`) - Highest precedence, committed to git
2. **User Skills** (`~/.gemini/skills/`) - Personal skills, available to all projects
3. **Extension Skills** - Bundled with installed extensions, lowest precedence

When duplicate names exist, higher precedence wins.

## Success Metrics

Feature is complete when:
1. `skilz install <skill> --agent gemini` installs to `.gemini/skills/`
2. `skilz install <skill> --agent gemini --user` installs to `~/.gemini/skills/`
3. Gemini CLI's `/skills list` shows Skilz-installed skills
4. Auto-detection works when `.gemini/` directory exists
5. Tests pass with 80%+ coverage for new code paths
6. Migration guide is published

## References

- [Gemini CLI Agent Skills Docs](https://code.gemini.com/docs/agent-skills) (assumed URL)
- [Agent Skills Open Standard](https://github.com/agentskills)
- [agentskills.io Spec](https://agentskills.io)
