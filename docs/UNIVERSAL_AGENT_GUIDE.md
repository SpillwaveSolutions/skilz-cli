# Universal Agent Guide

## Overview

The **Universal Agent** is a special agent type in Skilz that provides maximum flexibility for skill management. Unlike native agents (Claude, Gemini, Codex) that have specific directory structures and behaviors, the universal agent lets you:

- Install skills to custom locations
- Use custom configuration files
- Support multiple agents in the same project
- Work with legacy agent configurations

**When to Use Universal Agent:**
- Legacy Gemini workflow (without `experimental.skills` plugin)
- Multi-agent projects requiring shared skill documentation
- Custom config file workflows
- Projects needing explicit skill documentation in specific files

**When to Use Native Agents:**
- Single-agent projects (Claude, Gemini with native support, Codex)
- Simpler workflows without custom config needs
- Taking advantage of agent-specific optimizations

---

## Installation Modes

The universal agent supports two installation modes:

### User-Level Installation (Default)

Installs skills to `~/.skilz/skills/` for use across all projects.

```bash
skilz install <skill> --agent universal
# or simply (universal is default):
skilz install <skill>
```

**Directory Structure:**
```
~/.skilz/
└── skills/
    └── <skill-name>/
        └── SKILL.md
```

**No Config File:** User-level installations don't create/update config files.

---

### Project-Level Installation (NEW in 1.7)

Installs skills to `.skilz/skills/` within your project and creates/updates a configuration file.

```bash
skilz install <skill> --agent universal --project
```

**Directory Structure:**
```
my-project/
├── .skilz/
│   └── skills/
│       └── <skill-name>/
│           └── SKILL.md
└── AGENTS.md    # Created/updated automatically
```

**Default Config File:** `AGENTS.md` (auto-detected and created if needed)

---

### Custom Config File (NEW in 1.7)

Specify a custom configuration file for project-level installations.

```bash
skilz install <skill> --agent universal --project --config CUSTOM.md
```

**Directory Structure:**
```
my-project/
├── .skilz/
│   └── skills/
│       └── <skill-name>/
│           └── SKILL.md
└── CUSTOM.md    # Created/updated (NOT AGENTS.md)
```

**Requirements:**
- `--config` flag **requires** `--project` flag
- Can use any filename (e.g., `GEMINI.md`, `CUSTOM.md`, `AI_CONFIG.md`)
- Only the specified file is created/updated (overrides auto-detection)

---

## Basic Usage

### 1. Default Project Installation

Install a skill to your project using the default `AGENTS.md` config:

```bash
cd my-project
skilz install anthropics_skills/pdf-reader --agent universal --project
```

**What happens:**
1. Skill downloaded to `.skilz/skills/pdf-reader/`
2. `AGENTS.md` created (if doesn't exist)
3. Skill entry added to `AGENTS.md`

**AGENTS.md content:**
```markdown
# AGENTS.md

<skills_system priority="1">

## Available Skills

<available_skills>
- **pdf-reader**: Extract text and tables from PDF files
  - Invoke: `skilz read pdf-reader`
</available_skills>

</skills_system>
```

---

### 2. Custom Config File Installation

Install a skill using a custom config file:

```bash
cd my-project
skilz install anthropics_skills/excel --agent universal --project --config GEMINI.md
```

**What happens:**
1. Skill downloaded to `.skilz/skills/excel/`
2. `GEMINI.md` created (if doesn't exist)
3. Skill entry added to `GEMINI.md` (NOT `AGENTS.md`)

**GEMINI.md content:**
```markdown
# GEMINI.md

<skills_system priority="1">

## Available Skills

<available_skills>
- **excel**: Create and manipulate Excel spreadsheets
  - Invoke: `skilz read excel`
</available_skills>

</skills_system>
```

**Note:** `AGENTS.md` is NOT created or modified when using `--config`.

---

### 3. Multiple Skills in One Config

Install multiple skills to the same config file:

```bash
cd my-project
skilz install anthropics_skills/pdf-reader --agent universal --project --config GEMINI.md
skilz install anthropics_skills/excel --agent universal --project --config GEMINI.md
skilz install anthropics_skills/docx --agent universal --project --config GEMINI.md
```

**GEMINI.md content:**
```markdown
# GEMINI.md

<skills_system priority="1">

## Available Skills

<available_skills>
- **pdf-reader**: Extract text and tables from PDF files
  - Invoke: `skilz read pdf-reader`
- **excel**: Create and manipulate Excel spreadsheets
  - Invoke: `skilz read excel`
- **docx**: Create and edit Word documents
  - Invoke: `skilz read docx`
</available_skills>

</skills_system>
```

---

### 4. Multiple Config Files in One Project

Use different config files for different purposes:

```bash
cd my-project

# Skills for Gemini CLI (legacy mode)
skilz install anthropics_skills/pdf-reader --agent universal --project --config GEMINI.md
skilz install anthropics_skills/excel --agent universal --project --config GEMINI.md

# Skills for OpenCode
skilz install anthropics_skills/docx --agent universal --project --config AGENTS.md
skilz install anthropics_skills/plantuml --agent universal --project --config AGENTS.md

# Skills for custom agent
skilz install anthropics_skills/jira --agent universal --project --config CUSTOM_AGENT.md
```

**Project Structure:**
```
my-project/
├── .skilz/
│   └── skills/
│       ├── pdf-reader/
│       ├── excel/
│       ├── docx/
│       ├── plantuml/
│       └── jira/
├── GEMINI.md          # pdf-reader, excel
├── AGENTS.md          # docx, plantuml
└── CUSTOM_AGENT.md    # jira
```

Each config file only contains the skills you explicitly installed to it.

---

## Use Cases

### Use Case 1: Legacy Gemini Workflow

**Scenario:** You're using Gemini CLI without the `experimental.skills` plugin.

**Solution:** Use universal agent with custom `GEMINI.md` config:

```bash
cd my-ai-project

# Check if native Gemini support is available
skilz install test-skill --agent gemini --project
# If error: "Gemini does not support project-level installations"
# → Use universal agent instead

# Install skills for Gemini using universal agent
skilz install anthropics_skills/pdf-reader --agent universal --project --config GEMINI.md
skilz install anthropics_skills/excel --agent universal --project --config GEMINI.md
skilz install anthropics_skills/docx --agent universal --project --config GEMINI.md

# List installed skills
skilz list --agent universal --project
```

**Result:**
```
my-ai-project/
├── .skilz/
│   └── skills/
│       ├── pdf-reader/
│       ├── excel/
│       └── docx/
└── GEMINI.md    # All three skills documented here
```

**Gemini CLI will read:** `GEMINI.md` and load skills from `.skilz/skills/`

---

### Use Case 2: Multi-Agent Project with Shared Skills

**Scenario:** You're working on a project that uses multiple AI agents (Claude, Gemini, custom agents).

**Solution:** Use universal agent with different config files for each agent:

```bash
cd multi-agent-project

# Skills for Claude Code
skilz install anthropics_skills/pdf-reader --agent claude --project
# → Creates .claude/skills/pdf-reader/ (native)

# Skills for Gemini (legacy)
skilz install anthropics_skills/excel --agent universal --project --config GEMINI.md
skilz install anthropics_skills/docx --agent universal --project --config GEMINI.md

# Skills for OpenCode
skilz install anthropics_skills/plantuml --agent universal --project --config AGENTS.md
skilz install anthropics_skills/jira --agent universal --project --config AGENTS.md

# Skills for custom agent
skilz install anthropics_skills/confluence --agent universal --project --config CUSTOM.md
```

**Result:**
```
multi-agent-project/
├── .claude/
│   └── skills/
│       └── pdf-reader/        # Claude native
├── .skilz/
│   └── skills/
│       ├── excel/             # Universal (Gemini)
│       ├── docx/              # Universal (Gemini)
│       ├── plantuml/          # Universal (OpenCode)
│       ├── jira/              # Universal (OpenCode)
│       └── confluence/        # Universal (Custom)
├── GEMINI.md                  # excel, docx
├── AGENTS.md                  # plantuml, jira
└── CUSTOM.md                  # confluence
```

Each agent reads its own config file and loads the appropriate skills.

---

### Use Case 3: Explicit Skill Documentation

**Scenario:** You want to maintain explicit documentation of which skills are available in your project.

**Solution:** Use project-level universal agent installations:

```bash
cd documented-project

# Install skills with explicit documentation
skilz install anthropics_skills/pdf-reader --agent universal --project
skilz install anthropics_skills/excel --agent universal --project
skilz install anthropics_skills/docx --agent universal --project

# AGENTS.md is automatically maintained with skill list
cat AGENTS.md
```

**Benefit:** `AGENTS.md` serves as:
- Single source of truth for available skills
- Documentation for team members
- Version-controlled skill inventory
- Agent configuration reference

---

### Use Case 4: Migrating from Native to Universal

**Scenario:** You started with Gemini native support but need to switch to universal agent.

**Before (Gemini Native):**
```
my-project/
└── .gemini/
    └── skills/
        ├── pdf-reader/
        └── excel/
```

**Migration Steps:**
```bash
cd my-project

# Option 1: Keep using Gemini native (recommended if plugin available)
# No action needed

# Option 2: Switch to universal agent
# Remove old skills
skilz remove pdf-reader --agent gemini --project
skilz remove excel --agent gemini --project

# Install with universal agent
skilz install anthropics_skills/pdf-reader --agent universal --project --config GEMINI.md
skilz install anthropics_skills/excel --agent universal --project --config GEMINI.md
```

**After (Universal):**
```
my-project/
├── .skilz/
│   └── skills/
│       ├── pdf-reader/
│       └── excel/
└── GEMINI.md
```

**When to Migrate:**
- Lost access to `experimental.skills` plugin
- Need more control over skill locations
- Want to use multiple agents in same project
- Need custom config file organization

---

## Comparison with Native Agents

| Feature | Universal Agent | Native Agents (Claude/Gemini/Codex) |
|---------|----------------|-------------------------------------|
| **User Install Location** | `~/.skilz/skills/` | `~/.<agent>/skills/` |
| **Project Install Location** | `.skilz/skills/` | `.<agent>/skills/` |
| **Config File** | Required for project | Optional or None |
| **Custom Config** | Yes (`--config` flag) | No |
| **Multi-Agent Support** | Yes (multiple configs) | No (one agent per project) |
| **Flexibility** | High | Medium |
| **Simplicity** | Medium | High |
| **Agent Detection** | Manual (`--agent universal`) | Automatic (from directory) |
| **Native Integration** | No | Yes |
| **Project Installs** | Yes (as of 1.7.0) | Yes |
| **Custom Config Files** | Yes (as of 1.7.0) | No |

**Choose Universal Agent when:**
- You need custom config files
- You're using legacy Gemini workflow
- You want multiple agents in one project
- You need explicit skill documentation

**Choose Native Agent when:**
- You're using a single agent (Claude, Gemini with native support, Codex)
- You want simpler workflows
- You want automatic agent detection
- You prefer agent-native directory structures

---

## Detailed Examples

### Example 1: Single Skill Installation

**Goal:** Install one skill to a project using default config.

```bash
cd my-project
skilz install anthropics_skills/pdf-reader --agent universal --project
```

**Output:**
```
✓ Cloning skill repository...
✓ Installing skill: pdf-reader
✓ Skill installed to: .skilz/skills/pdf-reader
✓ Config updated: AGENTS.md
```

**Verification:**
```bash
# Check directory structure
ls -la .skilz/skills/pdf-reader/
# → SKILL.md

# Check config file
cat AGENTS.md
# → Contains pdf-reader entry

# List installed skills
skilz list --agent universal --project
# → pdf-reader
```

---

### Example 2: Multiple Skills, One Config

**Goal:** Install three skills to the same custom config file.

```bash
cd my-project

# Install skills one by one
skilz install anthropics_skills/pdf-reader --agent universal --project --config TOOLS.md
skilz install anthropics_skills/excel --agent universal --project --config TOOLS.md
skilz install anthropics_skills/docx --agent universal --project --config TOOLS.md
```

**Output (first install):**
```
✓ Cloning skill repository...
✓ Installing skill: pdf-reader
✓ Skill installed to: .skilz/skills/pdf-reader
✓ Config updated: TOOLS.md
```

**Output (subsequent installs):**
```
✓ Cloning skill repository...
✓ Installing skill: excel
✓ Skill installed to: .skilz/skills/excel
✓ Config updated: TOOLS.md (skill added)
```

**Verification:**
```bash
cat TOOLS.md
```

**TOOLS.md content:**
```markdown
# TOOLS.md

<skills_system priority="1">

## Available Skills

<available_skills>
- **pdf-reader**: Extract text and tables from PDF files
  - Invoke: `skilz read pdf-reader`
- **excel**: Create and manipulate Excel spreadsheets
  - Invoke: `skilz read excel`
- **docx**: Create and edit Word documents
  - Invoke: `skilz read docx`
</available_skills>

</skills_system>
```

---

### Example 3: Multiple Configs, Different Skills

**Goal:** Organize skills into different config files by purpose.

```bash
cd my-project

# Document processing skills
skilz install anthropics_skills/pdf-reader --agent universal --project --config DOCUMENTS.md
skilz install anthropics_skills/docx --agent universal --project --config DOCUMENTS.md

# Data analysis skills
skilz install anthropics_skills/excel --agent universal --project --config DATA.md
skilz install anthropics_skills/duckdb --agent universal --project --config DATA.md

# Collaboration skills
skilz install anthropics_skills/jira --agent universal --project --config COLLAB.md
skilz install anthropics_skills/confluence --agent universal --project --config COLLAB.md
```

**Project Structure:**
```
my-project/
├── .skilz/
│   └── skills/
│       ├── pdf-reader/
│       ├── docx/
│       ├── excel/
│       ├── duckdb/
│       ├── jira/
│       └── confluence/
├── DOCUMENTS.md    # pdf-reader, docx
├── DATA.md         # excel, duckdb
└── COLLAB.md       # jira, confluence
```

**List skills by config:**
```bash
# All universal skills in project
skilz list --agent universal --project
# → Shows all 6 skills

# Skills from specific config (manually check file)
grep "^- \*\*" DOCUMENTS.md
# → pdf-reader, docx
```

---

### Example 4: Removing Skills

**Goal:** Remove a skill from a custom config.

```bash
cd my-project

# Install skills
skilz install anthropics_skills/pdf-reader --agent universal --project --config TOOLS.md
skilz install anthropics_skills/excel --agent universal --project --config TOOLS.md

# Remove one skill
skilz remove pdf-reader --agent universal --project
```

**Output:**
```
✓ Removing skill: pdf-reader
✓ Skill removed from: .skilz/skills/pdf-reader
✓ Config updated: TOOLS.md (skill entry removed)
```

**TOOLS.md after removal:**
```markdown
# TOOLS.md

<skills_system priority="1">

## Available Skills

<available_skills>
- **excel**: Create and manipulate Excel spreadsheets
  - Invoke: `skilz read excel`
</available_skills>

</skills_system>
```

**Note:** Config file is automatically updated to remove the skill entry.

---

## Troubleshooting

### Issue 1: Config File Not Created

**Problem:** Installed skill but config file wasn't created.

**Possible Causes:**
1. Used user-level install (no `--project` flag)
2. File permissions issue
3. Already exists but not recognized

**Solution:**
```bash
# Verify you used --project flag
skilz install <skill> --agent universal --project --config CUSTOM.md

# Check if file was created
ls -la CUSTOM.md

# Check file permissions
ls -l CUSTOM.md
# Should be readable/writable

# Manually create if needed
touch CUSTOM.md
skilz install <skill> --agent universal --project --config CUSTOM.md
```

---

### Issue 2: Skills in Wrong Location

**Problem:** Skills installed to `~/.skilz/skills/` instead of `.skilz/skills/`.

**Cause:** Missing `--project` flag.

**Solution:**
```bash
# Wrong (user-level)
skilz install <skill> --agent universal

# Correct (project-level)
skilz install <skill> --agent universal --project
```

---

### Issue 3: Wrong Config File Updated

**Problem:** Installed with `--config CUSTOM.md` but `AGENTS.md` was updated.

**Cause:** This shouldn't happen in 1.7.0+. If it does, it's a bug.

**Solution:**
```bash
# Verify version
skilz --version
# Should be 1.7.0 or higher

# Try again with explicit paths
skilz install <skill> --agent universal --project --config ./CUSTOM.md

# If still broken, report bug at:
# https://github.com/spillwave/skilz-cli/issues
```

---

### Issue 4: Multiple Agents Conflict

**Problem:** Have both `.claude/skills/` and `.skilz/skills/` and unclear which is used.

**Explanation:** This is by design! Different agents read different locations:
- **Claude Code** reads `.claude/skills/` (native)
- **Gemini (native)** reads `.gemini/skills/` (native)
- **Universal agent** reads `.skilz/skills/` + config file

**Solution:** Each agent manages its own skills independently:
```bash
# Claude native skills
skilz list --agent claude --project

# Universal agent skills
skilz list --agent universal --project

# They don't conflict - each agent has its own set
```

---

### Issue 5: `--config` Requires `--project` Error

**Problem:** Got error "Error: --config flag requires --project flag".

**Cause:** Used `--config` without `--project`.

**Solution:**
```bash
# Wrong
skilz install <skill> --agent universal --config CUSTOM.md

# Correct
skilz install <skill> --agent universal --project --config CUSTOM.md
```

**Why:** Custom configs only make sense for project-level installs. User-level installs don't use config files.

---

### Issue 6: Skill Not Loading in Agent

**Problem:** Installed skill but AI agent doesn't recognize it.

**Possible Causes:**
1. Wrong config file name (agent expects different name)
2. Skill not properly documented in config
3. Agent not reading `.skilz/skills/` directory

**Solution:**
```bash
# 1. Check which config file your agent expects
# - Gemini CLI (legacy): GEMINI.md
# - OpenCode: AGENTS.md
# - Custom: Whatever you configured

# 2. Verify skill is in config file
cat AGENTS.md
# Should contain skill entry

# 3. Verify skill files exist
ls -la .skilz/skills/<skill-name>/
# Should contain SKILL.md

# 4. Re-read skill
skilz read <skill-name>
# Should output skill content

# 5. Reinstall if necessary
skilz remove <skill-name> --agent universal --project
skilz install <repo>/<skill-name> --agent universal --project --config AGENTS.md
```

---

## Best Practices

### When to Use `--config` Flag

**Use `--config` when:**
- Working with legacy Gemini (without native support)
- Organizing skills by purpose (DOCUMENTS.md, DATA.md, etc.)
- Supporting multiple agents in one project
- Need specific config file naming

**Don't use `--config` when:**
- Default `AGENTS.md` is fine
- Using native agent support (Claude, Gemini native, Codex)
- User-level installs (doesn't apply)

---

### Organizing Multi-Agent Projects

**Strategy 1: One Config Per Agent**
```
my-project/
├── CLAUDE.md       # Skills for Claude Code
├── GEMINI.md       # Skills for Gemini CLI
├── AGENTS.md       # Skills for OpenCode
└── .skilz/skills/  # All universal skills here
```

**Strategy 2: One Config Per Purpose**
```
my-project/
├── DOCUMENTS.md    # pdf-reader, docx, confluence
├── DATA.md         # excel, duckdb, postgresql
├── COLLAB.md       # jira, notion, github
└── .skilz/skills/  # All skills here
```

**Strategy 3: Hybrid Approach**
```
my-project/
├── .claude/skills/ # Native Claude skills
├── .gemini/skills/ # Native Gemini skills (if available)
├── AGENTS.md       # Universal skills for OpenCode
└── .skilz/skills/  # Universal skills shared across agents
```

---

### Config File Naming Conventions

**Recommended Names:**
- `AGENTS.md` - Default, works with OpenCode
- `GEMINI.md` - Legacy Gemini CLI
- `CLAUDE.md` - If using universal instead of Claude native
- `SKILLS.md` - Generic alternative
- `AI_TOOLS.md` - Descriptive name

**Avoid:**
- Generic names like `config.md` or `settings.md`
- Names that conflict with existing files
- Names with spaces or special characters

**Case Sensitivity:** Use uppercase for visibility (convention), but lowercase works too.

---

### Version Control

**Always Commit:**
- Config files (`AGENTS.md`, `GEMINI.md`, etc.)
- `.skilz/` directory structure (but not skill contents)

**Add to `.gitignore`:**
```
# .gitignore
.skilz/skills/*/SKILL.md  # Skill content (fetched from remote)
.skilz/skills/*/.git/     # Git metadata (if any)
```

**Rationale:**
- Config files document which skills are used
- Skill content can be re-fetched with `skilz update`
- Team members can clone repo and run `skilz update --all` to sync

---

### Updating Skills

**Update all universal skills in project:**
```bash
skilz update --all --agent universal --project
```

**Update specific skill:**
```bash
skilz update <skill-name> --agent universal --project
```

**After Update:**
- Config files are automatically maintained
- Skill content is refreshed from remote
- No manual changes needed

---

## Summary

The **universal agent** in Skilz 1.7+ provides powerful flexibility for managing AI agent skills:

**Key Features:**
- ✅ Project-level installations with custom config files
- ✅ Support for multiple agents in one project
- ✅ Legacy Gemini workflow support
- ✅ Explicit skill documentation in custom files
- ✅ Works alongside native agents (Claude, Gemini, Codex)

**Common Workflows:**
1. **Default project install:** `skilz install <skill> --agent universal --project`
2. **Custom config install:** `skilz install <skill> --agent universal --project --config CUSTOM.md`
3. **Legacy Gemini:** `skilz install <skill> --agent universal --project --config GEMINI.md`
4. **Multi-agent project:** Use different config files for each agent

**Best Practices:**
- Use native agents when available (simpler)
- Use universal agent for custom workflows
- Organize skills by purpose or agent
- Commit config files to version control
- Ignore skill content (re-fetchable)

**Learn More:**
- [USER_MANUAL.md](USER_MANUAL.md) - Complete user guide
- [GEMINI_MIGRATION.md](GEMINI_MIGRATION.md) - Gemini-specific migration guide
- [README.md](../README.md) - Quick start and examples

---

**Questions or Issues?**

Report issues at: https://github.com/spillwave/skilz-cli/issues
