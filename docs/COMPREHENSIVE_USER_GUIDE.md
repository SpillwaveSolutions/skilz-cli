# Skilz CLI - Comprehensive User Guide

**The Universal Package Manager for AI Skills**

[![PyPI version](https://badge.fury.io/py/skilz.svg)](https://pypi.org/project/skilz/)

Skilz is like npm or pip, but for AI coding assistants. It lets you install, manage, and share skills across 30+ AI agents from the AGENTS.md ecosystem, including Claude Code, OpenAI Codex, Gemini CLI, GitHub Copilot, Cursor, Aider, Windsurf, Zed AI, OpenHands, Cline, Goose, Roo Code, Google Antigravity, and many more.

**Browse skills:** [skillzwave.ai](https://skillzwave.ai) — The largest agent and agent skills marketplace
**Built by:** [Spillwave](https://spillwave.com) — Leaders in agentic software development

---

## Table of Contents

1. [Quick Start](#quick-start)
2. [Understanding Agents](#understanding-agents)
3. [Installation Modes: Copy vs Symlink](#installation-modes-copy-vs-symlink)
4. [User-Level vs Project-Level Installation](#user-level-vs-project-level-installation)
5. [Agent Reference](#agent-reference) | [Full Agent List](SUPPORTED_AGENTS.md)
6. [Command Reference](#command-reference)
7. [Search Paths and Resolution Order](#search-paths-and-resolution-order)
8. [Configuration File](#configuration-file)
9. [Common Workflows](#common-workflows)
10. [Troubleshooting](#troubleshooting)

---

## Quick Start

```bash
# Install skilz
pip install skilz

# Install a skill for Claude Code (user-level, available in all projects)
skilz install anthropics_skills/algorithmic-art

# Install a skill for Gemini CLI (project-level, in current directory)
skilz install anthropics_skills/brand-guidelines --agent gemini

# List installed skills
skilz list

# Read a skill (for AI agents to load)
skilz read algorithmic-art
```

---

## Understanding Agents

Skilz supports 30+ AI coding agents from the AGENTS.md ecosystem. Each agent has different capabilities:

| Agent | Display Name | Home Support | Native Skills | Default Mode |
|-------|--------------|--------------|---------------|--------------|
| `gemini` | Gemini CLI | ✅ Yes | All | copy |
| `opencode` | OpenCode CLI | ✅ Yes | All | copy |
| `openhands` | OpenHands | ✅ Yes | All | copy |
| `claude` | Claude Code | ✅ Yes | All | copy |
| `cline` | Cline | ✅ Yes | All | copy |
| `codex` | OpenAI Codex | ✅ Yes | All | copy |
| `goose` | Goose | ✅ Yes | All | copy |
| `roo` | Roo Code | ✅ Yes | All | copy |
| `kilo` | Kilo Code | ✅ Yes | All | copy |
| `trae` | Trae | ✅ Yes | All | copy |
| `droid` | Droid | ✅ Yes | All | copy |
| `clawdbot` | Clawdbot | ✅ Yes | All | copy |
| `kiro-cli` | Kiro CLI | ✅ Yes | All | copy |
| `pi` | Pi | ✅ Yes | All | copy |
| `neovate` | Neovate | ✅ Yes | All | copy |
| `antigravity` | Google Antigravity | ✅ Yes | All | copy |
| `cursor` | Cursor | ✅ Yes | All | copy |
| `windsurf` | Windsurf | ✅ Yes | All | copy |
| `copilot` | GitHub Copilot | ✅ Yes | All | copy |
| `qwen` | Qwen Code | ✅ Yes | All | copy |
| `zencoder` | Zencoder | ✅ Yes | All | copy |
| `amp` | Amp | ✅ Yes | All | copy |
| `qoder` | Qoder | ✅ Yes | All | copy |
| `command-code` | Command Code | ✅ Yes | All | copy |
| `universal` | Universal (Skilz) | ✅ Yes | None | copy |
| `aider` | Aider | ❌ No | None | copy |
| `zed` | Zed AI | ❌ No | None | copy |
| `crush` | Crush | ❌ No | None | copy |
| `kimi` | Kimi CLI | ❌ No | None | copy |
| `plandex` | Plandex | ❌ No | None | copy |

### What "Home Support" Means

- **Home Support = Yes**: Skills can be installed at the user level (e.g., `~/.claude/skills/`, `~/.gemini/skills/`) and are available across all projects
- **Home Support = No**: Skills must be installed per-project (in the current working directory)

### What "Native Skills" Means

- **All**: Agent has built-in skill loading and reads skills natively from their dedicated directories
- **Home only**: Agent loads skills from home directory only
- **None**: Agent needs config file injection to discover skills (uses universal bridge)

---

## Installation Modes: Copy vs Symlink

Skilz supports two ways to install skills:

### Copy Mode (Default for most agents)

```bash
skilz install spillwave/plantuml --copy
```

- **What happens**: Files are copied directly to the agent's skills directory
- **Pros**: Works with sandboxed tools (Gemini, etc.), self-contained, no external dependencies
- **Cons**: Uses more disk space if same skill installed in multiple projects

### Symlink Mode

```bash
skilz install spillwave/plantuml --symlink
```

- **What happens**: A symlink is created pointing to `~/.skilz/skills/<skill-name>`
- **Pros**: Saves disk space, updates apply everywhere automatically
- **Cons**: Doesn't work with workspace-sandboxed tools (Gemini can't follow symlinks outside project)

### When to Use Each

| Scenario | Recommended Mode |
|----------|------------------|
| Gemini CLI | **Copy** (workspace sandboxed) |
| GitHub Copilot | **Copy** (workspace sandboxed) |
| Claude Code | Copy or Symlink (both work) |
| OpenAI Codex | Copy or Symlink (both work) |
| OpenCode CLI | Copy or Symlink (both work) |
| OpenHands | Copy or Symlink (both work) |
| Cline, Goose, Roo, etc. | **Copy** (safer default) |
| Aider, Cursor, Windsurf | **Copy** (safer default) |
| Disk space constrained + Native agents | **Symlink** |

---

## Installing from Local Sources

In addition to installing from the registry, you can install skills directly from your local filesystem. This is perfect for:
- Testing new skills you are developing
- Sharing skills between different agents on the same machine
- Installing private skills not in any registry

### Usage

```bash
# Install from a local path
skilz install -f /path/to/skill [options]
```

### Examples: Sharing Skills Between Agents

If you have a skill installed for Claude Code but want to use it with Gemini CLI:

```bash
# Copy from Claude's skill directory to the current project for Gemini
skilz install -f ~/.claude/skills/design-doc-mermaid --project --agent gemini
```

If you have skills in OpenCode:

```bash
# Copy from OpenCode to current project
skilz install -f ~/.config/opencode/skill/sdd --project --agent gemini
```

From OpenAI Codex:

```bash
# Copy from Codex to current project
skilz install -f ~/.codex/skills/python-expert --project --agent gemini
```

Or from the Universal directory:

```bash
skilz install -f ~/.skilz/skills/my-tool --project --agent gemini
```

### Configuration Injection (The XML Part)

For agents that don't natively load skills (like Gemini, Qwen, etc.), Skilz injects an XML definition into the agent's context file (e.g., `GEMINI.md`).

After installing `design-doc-mermaid` for Gemini, your `GEMINI.md` will look like this:

```xml
<skills_system priority="1">

## Available Skills

<!-- SKILLS_TABLE_START -->
<usage>
When users ask you to perform tasks, check if any of the available skills
below can help complete the task more effectively.

How to use skills:
- Invoke: Bash("skilz read <skill-name>")
- The skill content will load with detailed instructions
- Base directory provided in output for resolving bundled resources
...
</usage>

<available_skills>

<skill>
<name>design-doc-mermaid</name>
<description>Create Mermaid diagrams for any purpose...</description>
<location>.skilz/skills/design-doc-mermaid/SKILL.md</location>
</skill>

</available_skills>
<!-- SKILLS_TABLE_END -->

</skills_system>
```

This tells the agent:
1. The skill exists and what it does (from the description)
2. Where the definition file is (`SKILL.md`)
3. How to use it (via `skilz read`)

---

## User-Level vs Project-Level Installation

### User-Level Installation (Default for supported agents)

Skills installed at the user level are available in ALL projects:

```bash
# Claude Code - installs to ~/.claude/skills/
skilz install anthropics_skills/theme-factory --agent claude

# OpenAI Codex - installs to ~/.codex/skills/
skilz install anthropics_skills/theme-factory --agent codex

# OpenCode CLI - installs to ~/.config/opencode/skill/
skilz install anthropics_skills/theme-factory --agent opencode

# Universal - installs to ~/.skilz/skills/
skilz install anthropics_skills/theme-factory --agent universal
```

### Project-Level Installation

Skills installed at the project level are only available in that project:

```bash
# Force project-level installation (any agent)
skilz install spillwave/plantuml --project

# Agents without home support always install to project level
skilz install spillwave/plantuml --agent gemini  # Always project-level
```

### Which Agents Support What

| Agent | User-Level Path | Project-Level Path |
|-------|-----------------|-------------------|
| `claude` | `~/.claude/skills/` | `.claude/skills/` |
| `codex` | `~/.codex/skills/` | `.codex/skills/` |
| `opencode` | `~/.config/opencode/skill/` | `.opencode/skill/` |
| `universal` | `~/.skilz/skills/` | `.skilz/skills/` |
| `gemini` | _(not supported)_ | `.skilz/skills/` |
| `copilot` | _(not supported)_ | `.github/skills/` |
| `cursor` | _(not supported)_ | `.skills/skills/` |
| `aider` | _(not supported)_ | `.skills/skills/` |
| `qwen` | _(not supported)_ | `.skills/skills/` |
| `windsurf` | _(not supported)_ | `.skills/skills/` |
| `kimi` | _(not supported)_ | `.skills/skills/` |
| `crush` | _(not supported)_ | `.skills/skills/` |
| `plandex` | _(not supported)_ | `.skills/skills/` |
| `zed` | _(not supported)_ | `.skills/skills/` |

---

## Agent Reference

### Claude Code

```bash
# User-level (recommended - available everywhere)
skilz install anthropics_skills/frontend-design --agent claude

# Project-level
skilz install anthropics_skills/frontend-design --agent claude --project

# List skills
skilz list --agent claude
```

**Paths:**
- User: `~/.claude/skills/`
- Project: `.claude/skills/`
- Config: `CLAUDE.md`

**Native skill support:** Full - Claude Code natively loads skills from both directories.

---

### OpenAI Codex

```bash
# User-level (recommended)
skilz install anthropics_skills/frontend-design --agent codex

# Project-level
skilz install anthropics_skills/frontend-design --agent codex --project

# List skills
skilz list --agent codex
```

**Paths:**
- User: `~/.codex/skills/`
- Project: `.codex/skills/`
- Config: `AGENTS.md`

**Native skill support:** Full - invoked via `$skill-name` or `/skills`.

---

### OpenCode CLI

```bash
# User-level
skilz install anthropics_skills/frontend-design --agent opencode

# Project-level
skilz install anthropics_skills/frontend-design --agent opencode --project

# List skills
skilz list --agent opencode
```

**Paths:**
- User: `~/.config/opencode/skill/`
- Project: `.skilz/skills/`
- Config: `AGENTS.md`

**Native skill support:** Home directory only.

---

### Gemini CLI

```bash
# Project-level only (no home support)
skilz install spillwave/plantuml --agent gemini

# With explicit copy mode (recommended, default)
skilz install spillwave/plantuml --agent gemini --copy

# List skills
skilz list --agent gemini --project
```

**Paths:**
- User: _(not supported)_
- Project: `.skilz/skills/`
- Config: `GEMINI.md`

**Important:** Gemini CLI uses workspace sandboxing and cannot follow symlinks outside the project. Always use `--copy` mode (the default).

**How skills are discovered:** Skilz updates `GEMINI.md` with skill references. Gemini reads this file and can invoke skills via `skilz read <skill-name>`.

---

### GitHub Copilot

```bash
# Project-level only
skilz install spillwave/plantuml --agent copilot

# List skills
skilz list --agent copilot --project
```

**Paths:**
- User: _(not supported)_
- Project: `.github/skills/` (native Copilot skills directory)
- Config: `.github/copilot-instructions.md`

**Native Support:** GitHub Copilot reads skills from `.github/skills/` natively (announced Dec 18, 2025). Config sync is skipped.

---

### Cursor

```bash
# Project-level only
skilz install spillwave/plantuml --agent cursor

# List skills
skilz list --agent cursor --project
```

**Paths:**
- User: _(not supported)_
- Project: `.skills/skills/`
- Config: `.cursor/rules/RULES.md`, `.cursor/rules/RULE.md`

**Note:** Cursor uses folder-based rules. Both config files are updated if they exist.

---

### Qwen CLI

```bash
# Project-level only
skilz install spillwave/plantuml --agent qwen

# List skills
skilz list --agent qwen --project
```

**Paths:**
- User: _(not supported)_
- Project: `.skills/skills/`
- Config: `QWEN.md` (primary), `CONTEXT.md` (secondary, only updated if exists)

---

### Universal (Skilz)

The universal agent is a fallback for tools that don't have specific support:

```bash
# User-level - skills go to ~/.skilz/skills/
skilz install spillwave/plantuml --agent universal

# Project-level
skilz install spillwave/plantuml --agent universal --project
```

**Paths:**
- User: `~/.skilz/skills/`
- Project: `.skilz/skills/`
- Config: _(none - no config file injection)_

**Use case:** Install skills centrally, then manually reference them or create symlinks for other tools.

---

### Other Agents (Aider, Windsurf, Kimi, Crush, Plandex, Zed)

All follow the same pattern:

```bash
skilz install spillwave/plantuml --agent aider
skilz install spillwave/plantuml --agent windsurf
skilz install spillwave/plantuml --agent kimi
skilz install spillwave/plantuml --agent crush
skilz install spillwave/plantuml --agent plandex
skilz install spillwave/plantuml --agent zed
```

**Paths:**
- User: _(not supported)_
- Project: `.skills/skills/`
- Config: Varies (see agent table)

---

## Command Reference

### Install

```bash
# Minimum command (auto-detects agent, defaults to claude)
skilz install <skill-id>

# Specify agent
skilz install <skill-id> --agent <agent>

# Force project-level
skilz install <skill-id> --project

# Force copy mode
skilz install <skill-id> --copy

# Force symlink mode
skilz install <skill-id> --symlink

# From local filesystem
skilz install -f /path/to/skill --agent gemini

# From git URL
skilz install -g https://github.com/user/skill-repo --agent claude
```

#### Version Control with `--version`

The `--version` flag lets you install specific versions of a skill:

```bash
# Install the marketplace version (default)
skilz install anthropics_skills/theme-factory

# Install latest from the default branch
skilz install anthropics_skills/theme-factory --version latest

# Install a specific git tag
skilz install anthropics_skills/theme-factory --version v1.0.0

# Install from a specific branch
skilz install anthropics_skills/theme-factory --version branch:develop

# Install a specific commit SHA
skilz install anthropics_skills/theme-factory --version abc123def456...
```

**Version Resolution Order:**

| Version Spec | What it Does |
|--------------|--------------|
| _(none)_ | Uses the marketplace/registry version (default, recommended) |
| `latest` | Gets the latest commit from the default branch |
| `v1.0.0` or `1.0.0` | Tries as a git tag (both with and without `v` prefix) |
| `branch:NAME` | Uses the latest commit from the specified branch |
| `40-char hex` | Uses the exact commit SHA |

**Fallback Behavior:**

If the GitHub API is unavailable or returns an error, skilz automatically:
1. Falls back to `HEAD` (latest commit)
2. Resolves the actual SHA after cloning
3. Tries multiple branch names if the specified branch doesn't exist (origin/HEAD, origin/main, origin/master)
4. Prints a warning so you know a fallback occurred

This ensures `skilz install` always works, even with flaky network conditions.

### List

```bash
# List all installed skills (auto-detect agent)
skilz list

# List for specific agent
skilz list --agent claude

# List project-level skills
skilz list --project

# Output as JSON
skilz list --json
```

### Read

```bash
# Read skill content (for AI agents to consume)
skilz read <skill-name>

# Read from specific agent
skilz read <skill-name> --agent gemini

# Read project-level skill
skilz read <skill-name> --project
```

### Update

```bash
# Update all skills
skilz update

# Update specific skill
skilz update <skill-id>

# Dry run (see what would change)
skilz update --dry-run
```

### Remove

```bash
# Remove a skill
skilz remove <skill-id>

# Skip confirmation
skilz remove <skill-id> -y

# Remove from project level
skilz remove <skill-id> --project
```

### Config

```bash
# Show configuration
skilz config

# Run interactive setup
skilz config --init
```

---

## Search Paths and Resolution Order

When Skilz looks for installed skills, it searches in this order:

### For Agents with Home Support (claude, codex, opencode, universal)

1. **User-level directory** (e.g., `~/.claude/skills/`)
2. **Project-level directory** (e.g., `.claude/skills/`)

### For Agents without Home Support (gemini, copilot, etc.)

1. **Project-level directory only** (e.g., `.skilz/skills/`)

### The `skilz read` Command

When you run `skilz read <skill-name>`:

1. First searches user-level (if supported)
2. Falls back to project-level
3. Returns skill content with base directory for resource resolution

---

## Configuration File

Skilz can be customized via `~/.config/skilz/config.json`:

```json
{
  "default_skills_dir": "~/.skilz/skills",
  "agents": {
    "mycompany": {
      "display_name": "MyCompany AI",
      "project_dir": ".mycompany/skills",
      "config_files": ["MYCOMPANY.md"],
      "supports_home": false,
      "default_mode": "copy",
      "native_skill_support": "none"
    }
  }
}
```

### Common Configuration Scenarios

#### OpenCode-Only Shop

If your team only uses OpenCode, you might want all skills in one place:

```json
{
  "default_skills_dir": "~/.config/opencode/skill"
}
```

#### Codex-Only Shop

```json
{
  "default_skills_dir": "~/.codex/skills"
}
```

#### Aider-Only Shop Using Universal

Since Aider doesn't support home-level skills, use the universal agent:

```bash
# Install skills centrally
skilz install spillwave/plantuml --agent universal

# Then in each project, create symlinks or copy
skilz install spillwave/plantuml --agent aider --project
```

Or configure to share the same project directory:

```json
{
  "agents": {
    "aider": {
      "display_name": "Aider",
      "project_dir": ".skilz/skills",
      "config_files": ["CONVENTIONS.md"],
      "supports_home": false,
      "default_mode": "copy",
      "native_skill_support": "none"
    }
  }
}
```

---

## Common Workflows

### Workflow 1: Claude Code User (Most Common)

```bash
# Install skills at user level - available everywhere
skilz install anthropics_skills/algorithmic-art
skilz install anthropics_skills/brand-guidelines
skilz install anthropics_skills/theme-factory

# List what you have
skilz list

# In any project, Claude Code will find them automatically
```

### Workflow 2: Gemini CLI User

```bash
# In your project directory
cd my-project

# Install skills (always project-level, always copy)
skilz install spillwave/plantuml --agent gemini
skilz install spillwave/sdd --agent gemini

# Gemini will see them in GEMINI.md
# Use: skilz read plantuml
```

### Workflow 3: Multi-Agent Project

```bash
cd my-project

# Install for multiple agents
skilz install spillwave/plantuml --agent claude --project
skilz install spillwave/plantuml --agent gemini
skilz install spillwave/plantuml --agent copilot

# Each agent gets its own copy in the right location
```

### Workflow 4: Sharing Skills Across Agents (Symlink Strategy)

```bash
# Install to universal directory first
skilz install spillwave/plantuml --agent universal

# Then create project-level symlinks for specific agents
skilz install spillwave/plantuml --agent claude --project --symlink
skilz install spillwave/plantuml --agent opencode --project --symlink

# Note: Don't use symlink for sandboxed agents (gemini, copilot)
skilz install spillwave/plantuml --agent gemini --copy  # Must be copy
```

### Workflow 5: CI/CD Scripting

```bash
# Use -y to skip all prompts
skilz -y install spillwave/plantuml --agent gemini
skilz -y remove old-skill --agent gemini
```

---

## Troubleshooting

### Skill Not Found After Install

**Symptoms:** `skilz list` shows the skill, but the AI agent can't find it.

**Solutions:**
1. Check you installed for the correct agent: `skilz list --agent <agent>`
2. For project-level installs, make sure you're in the right directory
3. For agents without native support, check the config file was updated (e.g., `GEMINI.md`)

### Gemini Can't Read Symlinked Skills

**Symptoms:** Gemini says it can't access the skill file.

**Solution:** Use copy mode instead of symlink:
```bash
skilz remove plantuml --agent gemini -y
skilz install spillwave/plantuml --agent gemini --copy
```

### Config File Not Updated

**Symptoms:** Skill installed but not appearing in `GEMINI.md` or other config file.

**Solutions:**
1. Reinstall: `skilz install <skill> --agent <agent>`
2. Check the config file location matches expectations
3. Manually add the skill reference if needed

### Broken Symlink

**Symptoms:** `skilz list` shows `[ERROR]` for a skill.

**Solution:** The symlink target was deleted. Remove and reinstall:
```bash
skilz remove broken-skill -y
skilz install <skill-id> --agent <agent>
```

### Wrong Agent Auto-Detected

**Symptoms:** Skills installing to wrong location.

**Solution:** Always specify the agent explicitly:
```bash
skilz install <skill> --agent gemini
```

---

## Next Steps

- **Browse skills:** [skillzwave.ai](https://skillzwave.ai) — The largest agent and agent skills marketplace
- Browse the [Skill Registry](https://github.com/SpillwaveSolutions/skilz-cli/blob/main/.skilz/registry.yaml)
- Create your own skills following the [agentskills.io standard](https://agentskills.io)
- Contribute to the [skilz-cli project](https://github.com/SpillwaveSolutions/skilz-cli)
- Learn more at [Spillwave](https://spillwave.com) — Leaders in agentic software development

---

_This guide covers Skilz CLI v1.2.0+. For the latest updates, see the [GitHub repository](https://github.com/SpillwaveSolutions/skilz-cli)._
