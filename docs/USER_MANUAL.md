# Skilz User Manual

**Version 1.10.0**

Skilz is the universal package manager for AI skills. It installs, manages, and updates skills across 30+ AI coding assistants including Claude Code, OpenCode, Gemini CLI, OpenHands, Cline, Goose, Roo Code, GitHub Copilot, Cursor, Windsurf, and many more.

**Browse skills:** [skillzwave.ai](https://skillzwave.ai) — The largest agent and agent skills marketplace
**Built by:** [Spillwave](https://spillwave.com) — Leaders in agentic software development

---

## Table of Contents

1. [Installation](#installation)
2. [Quick Start](#quick-start)
3. [Commands](#commands)
   - [skilz install](#skilz-install)
   - [skilz list](#skilz-list) (alias: `ls`)
   - [skilz update](#skilz-update)
   - [skilz uninstall](#skilz-uninstall) (alias: `rm`)
   - [skilz search](#skilz-search) (NEW)
   - [skilz visit](#skilz-visit) (NEW)
   - [skilz config](#skilz-config)
4. [Configuration](#configuration)
   - [Config File](#config-file)
   - [Environment Variables](#environment-variables)
   - [Override Hierarchy](#override-hierarchy)
   - [Registry Files](#registry-files)
   - [Manifest Files](#manifest-files)
5. [Shell Completion](#shell-completion)
6. [Global Flags](#global-flags)
7. [Working with Multiple Agents](#working-with-multiple-agents)
   - [Gemini CLI Support (NEW in 1.7)](#gemini-cli-support-new-in-17)
   - [Universal Agent Custom Config (NEW in 1.7)](#universal-agent-custom-config-new-in-17)
8. [Project vs User Level Installation](#project-vs-user-level-installation)
9. [Scripting & Automation](#scripting--automation)
10. [Troubleshooting](#troubleshooting)
11. [Examples](#examples)
12. [Development](#development)

---

## Installation

### From PyPI (Recommended)

```bash
pip install skilz
```

### From GitHub

```bash
# Install directly from GitHub (latest development version)
pip install git+https://github.com/spillwave/skilz-cli.git

# Or clone and install
git clone https://github.com/spillwave/skilz-cli.git
cd skilz-cli
pip install .
```

### Verify Installation

```bash
skilz --version
```

### Development Setup

For contributors or local development:

```bash
git clone https://github.com/spillwave/skilz-cli.git
cd skilz-cli

# Option 1: Using Task (recommended)
task install

# Option 2: Using pip
pip install -e ".[dev]"
```

See [Development](#development) for available development commands.

---

## Quick Start

```bash
# Install a skill from the marketplace
skilz install anthropics_skills/algorithmic-art

# Install directly from GitHub URL (NEW in 1.5 - no -g flag needed)
skilz install https://github.com/owner/repo

# Search for skills on GitHub (NEW in 1.5)
skilz search excel

# See what's installed (alias: skilz ls)
skilz list

# Update all skills to latest versions
skilz update

# Uninstall a skill you no longer need (alias: skilz rm)
skilz uninstall algorithmic-art
```

---

## Commands

### skilz install

Install a skill from the registry.

**Syntax:**
```bash
skilz install <skill-id> [options]
```

**Arguments:**
| Argument | Description |
|----------|-------------|
| `skill-id` | The skill identifier (e.g., `anthropics_skills/theme-factory`) |

**Options:**
| Option | Description |
|--------|-------------|
| `--agent {gemini,opencode,openhands,claude,cline,codex,goose,roo,kilo,trae,droid,clawdbot,kiro-cli,pi,neovate,antigravity,cursor,windsurf,copilot,qwen,zencoder,amp,qoder,command-code,universal,aider,zed,crush,kimi,plandex}` | Target agent. Auto-detected if not specified. |
| `--project` | Install to project directory instead of user directory |
| `-f, --file PATH` | Install from local filesystem path |
| `-g, --git URL` | Install from Git repository URL |
| `--copy` | Force copy installation (default for project-level) |
| `--symlink` | Force symlink installation (default for user-level) |
| `-v, --verbose` | Show detailed output |

**Examples:**

```bash
# Basic install (auto-detects agent)
skilz install anthropics_skills/theme-factory

# Install for specific agent
skilz install anthropics_skills/theme-factory --agent claude
skilz install anthropics_skills/theme-factory --agent opencode
skilz install anthropics_skills/theme-factory --agent gemini
skilz install anthropics_skills/theme-factory --agent openhands
skilz install anthropics_skills/theme-factory --agent cline

# Install from local filesystem
skilz install -f ~/.claude/skills/design-doc-mermaid --project --agent gemini

# Install from git repository (URL)
skilz install -g https://github.com/user/skill-repo.git

# Install to project directory (for testing or project-specific skills)
skilz install anthropics_skills/theme-factory --project

# Verbose output to see what's happening
skilz install anthropics_skills/theme-factory -v
```

**What happens during install:**

1. Skilz looks up the skill ID in the registry or marketplace API
2. Clones the Git repository (or uses cached clone)
3. Checks out the specific commit SHA from the registry
4. Copies the skill files to the appropriate skills directory
5. Writes a manifest file for tracking

**Idempotent behavior:**

If the skill is already installed with the same SHA, Skilz skips the installation:
```
Already installed: anthropics_skills/theme-factory (00756142)
```

---

### NEW Marketplace Format (NEW in 1.7)

Skilz 1.7+ supports a new intuitive skill ID format that mirrors GitHub's URL structure:

**Supported Formats:**

| Format | Example | Description |
|--------|---------|-------------|
| **NEW** | `owner/repo/skill` | Intuitive GitHub-style format |
| **LEGACY** | `owner_repo/skill` | Original underscore format |
| **SLUG** | `owner__repo__skill` | Direct Firestore document ID |

**All formats are REST-first** - they try the skillzwave.ai REST API before falling back to GitHub.

**Examples:**

```bash
# NEW format (recommended)
skilz install anthropics/skills/algorithmic-art

# LEGACY format (backwards compatible)
skilz install anthropics_skills/algorithmic-art

# SLUG format (direct Firestore ID)
skilz install anthropics__skills__algorithmic-art

# Verbose mode shows format detection
skilz install anthropics/skills/algorithmic-art -v
# Output: Detected format: NEW, attempting REST lookup...
```

---

### Installing Local Skills

You can install skills directly from your local filesystem. This is useful for developing new skills or installing skills from other agent directories (like Claude or OpenCode).

**Syntax:**
```bash
skilz install -f <path-to-skill> [options]
```

**Examples:**

```bash
# Install a skill from Claude Code's directory to a project for Gemini
skilz install -f ~/.claude/skills/design-doc-mermaid --project --agent gemini

# Install a skill from OpenCode's directory
skilz install -f ~/.config/opencode/skills/my-skill --project --agent gemini

# Install a skill from a universal installation
skilz install -f ~/.skilz/skills/some-tool --project --agent universal
```

**What happens to config files (e.g., GEMINI.md):**

When you install a skill for an agent like Gemini (which doesn't have native skill loading), Skilz automatically injects the skill definition into the agent's context file (e.g., `GEMINI.md`).

After running:
`skilz install -f ~/.claude/skills/design-doc-mermaid --project --agent gemini`

Your `GEMINI.md` will contain:

```xml
<skills_system priority="1">

## Available Skills

<!-- SKILLS_TABLE_START -->
<usage>
When users ask you to perform tasks, check if any of the available skills
below can help complete the task more effectively.
...
</usage>

<available_skills>

<skill>
<name>design-doc-mermaid</name>
<description>Create Mermaid diagrams for any purpose - activity diagrams, deployment diagrams, architecture diagrams, or complete design documents.</description>
<location>.skilz/skills/design-doc-mermaid/SKILL.md</location>
</skill>

</available_skills>
<!-- SKILLS_TABLE_END -->

</skills_system>
```

The agent (Gemini) reads this section and knows how to invoke the skill using `skilz read design-doc-mermaid`.

---

### skilz list

Show all installed skills with their versions and status.

**Syntax:**
```bash
skilz list [options]
```

**Options:**
| Option | Description |
|--------|-------------|
| `--agent {gemini,opencode,openhands,claude,cline,...}` | Filter by agent type |
| `--project` | List project-level skills instead of user-level |
| `--all` | Scan all agents (default: top 5) |
| `--json` | Output as JSON (for scripting) |
| `-v, --verbose` | Show detailed output |

**Examples:**

```bash
# List all user-level skills
skilz list

# List project-level skills
skilz list --project

# List only Claude Code skills
skilz list --agent claude

# List skills from all agents (not just top 5)
skilz list --all

# Get JSON output for scripting
skilz list --json
```

**Table Output:**

```
Agent         Skill                               Version   Mode     Status
────────────────────────────────────────────────────────────────────────────────
Claude Code   anthropics_skills/algorithmic-art   00756142  [copy]   up-to-date
OpenAI Codex  anthropics_skills/brand-guidelines  f2489dcd  [copy]   up-to-date
Claude Code   anthropics_skills/theme-factory     e1c29a38  [copy]   outdated
```

**Status Values:**

| Status | Meaning |
|--------|---------|
| `up-to-date` | Installed SHA matches registry SHA |
| `outdated` | Registry has a newer SHA |
| `unknown` | Skill not found in registry |

**JSON Output:**

```json
[
  {
    "skill_id": "anthropics_skills/algorithmic-art",
    "skill_name": "algorithmic-art",
    "git_sha": "00756142ab04c82a447693cf373c4e0c554d1005",
    "installed_at": "2025-01-15T14:32:00+00:00",
    "status": "up-to-date",
    "path": "/Users/you/.claude/skills/algorithmic-art",
    "agent": "claude",
    "agent_display_name": "Claude Code",
    "project_level": false
  }
]
```

---

### skilz update

Update installed skills to their latest registry versions.

**Syntax:**
```bash
skilz update [skill-id] [options]
```

**Arguments:**
| Argument | Description |
|----------|-------------|
| `skill-id` | Optional. Update only this skill. Updates all if omitted. |

**Options:**
| Option | Description |
|--------|-------------|
| `--agent {gemini,opencode,openhands,claude,cline,...}` | Filter by agent type |
| `--project` | Update project-level skills instead of user-level |
| `--dry-run` | Show what would be updated without making changes |
| `-v, --verbose` | Show detailed output |

**Examples:**

```bash
# Update all skills
skilz update

# Update a specific skill
skilz update anthropics_skills/theme-factory

# Preview what would be updated
skilz update --dry-run

# Update project-level skills
skilz update --project

# Update only Claude Code skills
skilz update --agent claude
```

**Output:**

```
Checking 3 installed skill(s)...
  anthropics_skills/algorithmic-art: up-to-date (00756142)
  anthropics_skills/brand-guidelines: updating f2489dcd -> a1b2c3d4
  anthropics_skills/theme-factory: up-to-date (e1c29a38)

Updated 1 skill(s), 2 already up-to-date
```

**Dry-run Output:**

```
Checking 3 installed skill(s)...
  anthropics_skills/algorithmic-art: up-to-date (00756142)
  anthropics_skills/brand-guidelines: would update f2489dcd -> a1b2c3d4
  anthropics_skills/theme-factory: up-to-date (e1c29a38)

Would update 1 skill(s), 2 already up-to-date
```

---

### skilz uninstall (alias: rm)

Uninstall an installed skill. The `remove` command is still available as an alias for backward compatibility.

**Syntax:**
```bash
skilz uninstall <skill-id> [options]
skilz rm <skill-id> [options]  # Unix-style alias
```

**Arguments:**
| Argument | Description |
|----------|-------------|
| `skill-id` | The skill to uninstall (full ID or just the name) |

**Options:**
| Option | Description |
|--------|-------------|
| `--agent {gemini,opencode,openhands,claude,cline,...}` | Filter by agent type |
| `--project` | Uninstall from project-level instead of user-level |
| `-y, --yes` | Skip confirmation prompt |
| `-v, --verbose` | Show detailed output |

**Examples:**

```bash
# Uninstall with confirmation prompt
skilz uninstall anthropics_skills/theme-factory

# Using rm alias
skilz rm theme-factory

# Skip confirmation (useful for scripts)
skilz rm theme-factory -y

# Uninstall from project directory
skilz rm algorithmic-art --project --yes
```

**Confirmation Prompt:**

```
Remove anthropics_skills/theme-factory from Claude Code? [y/N] y
Removed: anthropics_skills/theme-factory
```

**Finding Skills by Name:**

You can use partial names if they're unambiguous:

```bash
# These all work if there's only one matching skill:
skilz rm anthropics_skills/theme-factory  # Full ID
skilz rm theme-factory                    # Name only
skilz rm factory                          # Partial match
```

If the partial match is ambiguous, Skilz will report an error.

---

### skilz search (NEW in 1.5)

Search GitHub for available skills.

**Syntax:**
```bash
skilz search <query> [options]
```

**Arguments:**
| Argument | Description |
|----------|-------------|
| `query` | Search query (e.g., 'excel', 'pdf', 'data analysis') |

**Options:**
| Option | Description |
|--------|-------------|
| `-l, --limit` | Maximum number of results (default: 10) |
| `--json` | Output as JSON for scripting |

**Examples:**

```bash
# Basic search
skilz search excel

# Limit results
skilz search pdf --limit 5

# Multi-word queries (use quotes)
skilz search "data analysis"

# JSON output for scripting
skilz search excel --json
```

**Output:**

```
Found 10 skill(s) matching 'excel':

NAME                          STARS  DESCRIPTION
--------------------------------------------------------------------------------
anthropics/excel-skills          150  Excel manipulation for Claude
user/spreadsheet-tools            45  Create and edit spreadsheets
...
```

**Requirements:**
- Requires [GitHub CLI (`gh`)](https://cli.github.com) for best results
- Works unauthenticated, but authenticated provides better rate limits

---

### skilz visit (NEW in 1.5)

Open a skill's GitHub page in your default browser.

**Syntax:**
```bash
skilz visit <source>
```

**Arguments:**
| Argument | Description |
|----------|-------------|
| `source` | Repository path or URL to visit |

**Source Formats:**
| Format | Opens |
|--------|-------|
| `owner/repo` | Repository page |
| `owner/repo/skill` | Skill directory in repo |
| `https://...` | Full URL directly |

**Examples:**

```bash
# Open repository page
skilz visit anthropics/skills

# Open skill directory
skilz visit anthropics/skills/excel

# Open full URL
skilz visit https://github.com/user/repo
```

**Output:**

```
Opening: https://github.com/anthropics/skills
```

---

### Command Aliases (NEW in 1.5)

For Unix-like familiarity, Skilz provides these command aliases:

| Original | Alias | Example |
|----------|-------|---------|
| `skilz list` | `skilz ls` | `skilz ls --json` |
| `skilz uninstall` | `skilz rm` | `skilz rm my-skill -y` |

---

### skilz config

View and modify Skilz configuration.

**Syntax:**
```bash
skilz config [options]
```

**Options:**
| Option | Description |
|--------|-------------|
| `--init` | Run interactive configuration setup |
| `-v, --verbose` | Show detailed output |

**Examples:**

```bash
# Show current configuration
skilz config

# Run interactive setup wizard
skilz config --init

# Use defaults without prompts (for scripting)
skilz -y config --init
```

**Show Configuration:**

```
$ skilz config
Configuration: ~/.config/skilz/settings.json

Setting              Config File        Env Override       Effective
----------------------------------------------------------------------------
claude_code_home     (not set)          (not set)          /Users/you/.claude
open_code_home       (not set)          (not set)          /Users/you/.config/opencode
agent_default        opencode           (not set)          opencode

Use 'skilz config --init' to create or modify configuration.
```

**Interactive Setup:**

```
$ skilz config --init

Skilz Configuration Setup
--------------------------

Claude Code home [~/.claude]:
OpenCode home [~/.config/opencode]:
Default agent (claude/opencode/auto) [auto]: opencode

Install shell completion?
  [1] zsh (~/.zshrc)
  [2] bash (~/.bashrc)
  [3] Skip

Choice [1]: 1
Added completion to ~/.zshrc

Configuration saved to ~/.config/skilz/settings.json
```

---

## Configuration

### Config File

Skilz stores configuration in `~/.config/skilz/settings.json`:

```json
{
  "claude_code_home": "/custom/path/to/claude",
  "open_code_home": "/custom/path/to/opencode",
  "agent_default": "opencode"
}
```

**Configuration Settings:**

| Setting | Description | Default |
|---------|-------------|---------|
| `claude_code_home` | Claude Code home directory | `~/.claude` |
| `open_code_home` | OpenCode home directory | `~/.config/opencode` |
| `agent_default` | Default agent for commands | `null` (auto-detect) |

Setting `agent_default` to `"opencode"` means you won't need to type `--agent opencode` on every command.

### Environment Variables

Environment variables override config file values:

| Variable | Overrides |
|----------|-----------|
| `CLAUDE_CODE_HOME` | `claude_code_home` config |
| `OPEN_CODE_HOME` | `open_code_home` config |
| `AGENT_DEFAULT` | `agent_default` config |

**Examples:**

```bash
# Override Claude Code home for this session
export CLAUDE_CODE_HOME=/opt/claude
skilz install plantuml

# Override default agent for this command
AGENT_DEFAULT=opencode skilz list
```

### Override Hierarchy

Configuration values are resolved in this order (lowest to highest priority):

1. **Default values** - Built-in defaults
2. **Config file** - `~/.config/skilz/settings.json`
3. **Environment variables** - `CLAUDE_CODE_HOME`, etc.
4. **Command line** - `--agent` flag

Example: If your config file has `agent_default: claude`, but you set `AGENT_DEFAULT=opencode` in your shell, then opencode will be used. But if you also add `--agent claude` to your command, claude will be used.

### Registry Files

Skilz reads skill definitions from registry files in YAML format.

**Registry Locations (in priority order):**

| Location | Scope |
|----------|-------|
| `.skilz/registry.yaml` | Project-level (current directory) |
| `~/.skilz/registry.yaml` | User-level (home directory) |

**Registry Format:**

```yaml
# .skilz/registry.yaml

anthropics_skills/algorithmic-art:
  git_repo: https://github.com/anthropics/skills.git
  skill_path: /main/skills/algorithmic-art/SKILL.md
  git_sha: 00756142ab04c82a447693cf373c4e0c554d1005

anthropics_skills/brand-guidelines:
  git_repo: https://github.com/anthropics/skills.git
  skill_path: /main/skills/brand-guidelines/SKILL.md
  git_sha: 00756142ab04c82a447693cf373c4e0c554d1005

anthropics_skills/theme-factory:
  git_repo: https://github.com/anthropics/skills.git
  skill_path: /main/skills/theme-factory/SKILL.md
  git_sha: 00756142ab04c82a447693cf373c4e0c554d1005
```

**Registry Fields:**

| Field | Required | Description |
|-------|----------|-------------|
| `git_repo` | Yes | Git repository URL (HTTPS or SSH) |
| `skill_path` | Yes | Path to skill within repo (includes branch/tag) |
| `git_sha` | Yes | Full 40-character commit SHA |

### Manifest Files

When Skilz installs a skill, it creates a `.skilz-manifest.yaml` file in the skill directory:

```yaml
installed_at: 2025-01-15T14:32:00+00:00
skill_id: anthropics_skills/theme-factory
git_repo: https://github.com/anthropics/skills.git
skill_path: /main/skills/theme-factory/SKILL.md
git_sha: 00756142ab04c82a447693cf373c4e0c554d1005
skilz_version: 0.1.0
```

**Why manifests matter:**

- **Auditing**: Know exactly what's installed and where it came from
- **Updates**: Compare installed SHA to registry to detect outdated skills
- **Troubleshooting**: Trace issues to specific commits

---

## Shell Completion

Skilz supports shell completion for both zsh and bash.

### Installation via Config

The easiest way to install completion is via the config wizard:

```bash
skilz config --init
```

Select your shell when prompted.

### Manual Installation

**For zsh:**

```bash
# Create completion directory
mkdir -p ~/.zfunc

# Generate completion script
skilz config --init  # Select zsh option

# Or add to .zshrc manually:
fpath=(~/.zfunc $fpath)
autoload -Uz compinit && compinit
```

**For bash:**

```bash
# Create completion directory
mkdir -p ~/.local/share/bash-completion/completions

# Generate completion script
skilz config --init  # Select bash option
```

After installation, restart your shell or source your RC file.

---

## Global Flags

These flags can be used with any command:

| Flag | Description |
|------|-------------|
| `-V, --version` | Show version and exit |
| `-v, --verbose` | Enable verbose output |
| `-y, --yes-all` | Skip all confirmation prompts (for scripting) |
| `-h, --help` | Show help message |

**The `-y` flag is especially useful for automation:**

```bash
# Remove without confirmation
skilz -y remove plantuml

# Non-interactive config setup
skilz -y config --init
```

---

## Working with Multiple Agents

Skilz supports multiple AI coding assistants. Use `--agent` to target a specific one:

| Agent | Skills Directory | Notes |
|-------|------------------|-------|
| `claude` | `~/.claude/skills/` or `.claude/skills/` | Native support |
| `codex` | `~/.codex/skills/` or `.codex/skills/` | Native support |
| `opencode` | `~/.config/opencode/skill/` or `.opencode/skill/` | Native support |
| `gemini` | `~/.gemini/skills/` or `.gemini/skills/` | Native support (requires plugin) |
| `copilot` | `.github/skills/` | Project-level only |
| `cursor` | `.cursor/skills/` | Project-level only |
| `aider` | `~/.aider/skills/` | User-level |
| `windsurf` | `~/.windsurf/skills/` | User-level |
| `qwen` | `~/.qwen/skills/` | User-level |
| `kimi` | `~/.kimi/skills/` | User-level |
| `crush` | `~/.crush/skills/` | User-level |
| `plandex` | `~/.plandex/skills/` | User-level |
| `zed` | `~/.zed/skills/` | User-level |
| `universal` | `~/.skilz/skills/` or `.skilz/skills/` | Universal fallback |

**Auto-detection:**

If you don't specify `--agent`, Skilz auto-detects based on:
1. Presence of `.claude/` in current directory
2. Presence of `.gemini/` in current directory
3. Presence of `.codex/` in current directory
4. Presence of `~/.claude/` (user has Claude Code)
5. Presence of `~/.gemini/` (user has Gemini CLI)
6. Presence of `~/.codex/` (user has OpenAI Codex)
7. Presence of `~/.config/opencode/` (user has OpenCode)
8. Defaults to `claude` if none detected

**Installing to multiple agents:**

```bash
# Install to multiple agents
skilz install plantuml --agent claude
skilz install plantuml --agent opencode
skilz install plantuml --agent gemini
skilz install plantuml --agent openhands
skilz install plantuml --agent cline
```

### Gemini CLI Support (NEW in 1.7)

Skilz 1.7+ supports two modes for Gemini CLI:

#### Native Support (Recommended)

**Requirements:** Gemini CLI with `experimental.skills` plugin installed.

**Features:**
- Project-level: `.gemini/skills/`
- User-level: `~/.gemini/skills/`
- No config file needed (Gemini reads skills directly)

**Example:**
```bash
# Install to Gemini (native mode)
skilz install anthropics_skills/pdf-reader --agent gemini --project

# Skill is installed to:
# .gemini/skills/pdf-reader/

# Gemini CLI automatically detects and loads the skill
```

**When to use:** If you have the `experimental.skills` plugin, this is the recommended approach.

---

#### Legacy Mode (Universal Agent)

**For users without `experimental.skills` plugin.**

**Features:**
- Project-level: `.skilz/skills/`
- Config file: `GEMINI.md` (requires `--config` flag)
- Manual skill documentation in config

**Example:**
```bash
# Install using universal agent with Gemini config
skilz install anthropics_skills/pdf-reader --agent universal --project --config GEMINI.md

# Skill is installed to:
# .skilz/skills/pdf-reader/
# GEMINI.md is created/updated with skill entry

# Configure Gemini CLI to read GEMINI.md
```

**When to use:** If you don't have the `experimental.skills` plugin or prefer explicit config files.

---

**How to check which mode you have:**

```bash
# Try native installation
skilz install test-skill --agent gemini --project

# If successful → You have native support
# If error "Gemini does not support project-level installations" → Use legacy mode
```

**Migration Guide:** See [GEMINI_MIGRATION.md](GEMINI_MIGRATION.md) for detailed migration instructions.

---

### Universal Agent Custom Config (NEW in 1.7)

The universal agent now supports project-level installations with custom configuration files.

#### Default Behavior

```bash
skilz install <skill> --agent universal --project
# Creates/updates: AGENTS.md
# Skill location: .skilz/skills/<skill>/
```

#### Custom Config File

```bash
skilz install <skill> --agent universal --project --config GEMINI.md
# Creates/updates: GEMINI.md (not AGENTS.md)
# Skill location: .skilz/skills/<skill>/
```

#### Requirements

- `--config` flag **requires** `--project` flag
- Works with any filename (e.g., `GEMINI.md`, `CUSTOM.md`, `AI_CONFIG.md`)
- Only the specified file is updated (overrides auto-detection)

#### Use Cases

1. **Legacy Gemini workflow** (without native plugin support)
2. **Multi-agent projects** with different config files per agent
3. **Custom organization** (e.g., `DOCUMENTS.md`, `DATA.md`, etc.)
4. **Explicit documentation** of available skills

**Complete Guide:** See [UNIVERSAL_AGENT_GUIDE.md](UNIVERSAL_AGENT_GUIDE.md) for detailed examples and use cases.

---

## Project vs User Level Installation

**User-level** (default): Skills installed to your home directory, available globally.

**Project-level** (`--project`): Skills installed to the current project directory, only available in that project.

| Level | Claude Code | OpenCode |
|-------|-------------|----------|
| User | `~/.claude/skills/` | `~/.config/opencode/skill/` |
| Project | `.claude/skills/` | `.opencode/skill/` |

**When to use project-level:**

- Testing skills before global installation
- Project-specific skills not needed elsewhere
- Team collaboration (commit `.claude/skills/` to version control)

```bash
# Install to project
skilz install plantuml --project

# List project skills
skilz list --project

# Update project skills
skilz update --project

# Remove from project
skilz remove plantuml --project
```

---

## Scripting & Automation

Skilz is designed for use in scripts and automation pipelines.

### Non-Interactive Mode

Use `-y` or `--yes-all` to skip all confirmation prompts:

```bash
#!/bin/bash
# install-skills.sh - Install standard skills without prompts

skilz -y install anthropics_skills/algorithmic-art
skilz -y install anthropics_skills/brand-guidelines
skilz -y install anthropics_skills/theme-factory
```

### JSON Output for Scripting

Use `--json` with list to get machine-parseable output:

```bash
# Get all outdated skills
skilz list --json | jq -r '.[] | select(.status == "outdated") | .skill_id'

# Count installed skills
skilz list --json | jq length

# Check if a specific skill is installed
if skilz list --json | jq -e '.[] | select(.skill_id == "anthropics_skills/algorithmic-art")' > /dev/null; then
    echo "algorithmic-art is installed"
fi
```

### Environment Variables

Use environment variables to control skilz behavior without modifying config:

```bash
# CI/CD pipeline example
export CLAUDE_CODE_HOME=/app/.claude
export AGENT_DEFAULT=claude

skilz install plantuml
skilz list
```

### Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | Error (skill not found, git failure, permission denied, etc.) |

Use exit codes in scripts:

```bash
if skilz install my-skill; then
    echo "Installation successful"
else
    echo "Installation failed"
    exit 1
fi
```

### Idempotent Operations

All skilz operations are idempotent - running them multiple times produces the same result:

```bash
# Safe to run in CI/CD - won't reinstall if already at correct version
skilz install anthropics_skills/theme-factory
skilz install anthropics_skills/theme-factory  # No-op

# Update is also idempotent
skilz update  # Only updates outdated skills
skilz update  # No-op if all up-to-date
```

---

## Troubleshooting

### Skill not found

```
Error: Skill 'unknown/skill' not found in registry.
Searched: .skilz/registry.yaml, ~/.skilz/registry.yaml
```

**Solution:** Check that the skill ID exists in your registry file.

### Git clone failed

```
Error: Failed to clone repository
```

**Solutions:**
- Check your network connection
- Verify the Git URL is correct
- For SSH URLs, ensure your SSH keys are configured
- For private repos, ensure you have access

### Permission denied

```
Error: Permission denied: /path/to/skills
```

**Solution:** Check directory permissions or try with `--project` to install locally.

### Skill already installed

```
Already installed: anthropics_skills/theme-factory (00756142)
```

This is normal behavior. Skilz is idempotent and skips reinstallation if the SHA matches.

### Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | Error (skill not found, git failure, etc.) |

---

## Examples

### Setting up a new project

```bash
# Create project registry
mkdir -p .skilz
cat > .skilz/registry.yaml << 'EOF'
team/my-skill:
  git_repo: https://github.com/myteam/skills.git
  skill_path: /main/my-skill/SKILL.md
  git_sha: abc123def456789012345678901234567890abcd
EOF

# Install to project
skilz install team/my-skill --project

# Verify
skilz list --project
```

### Updating all skills in CI/CD

```bash
#!/bin/bash
# update-skills.sh

# Show what would be updated
skilz update --dry-run

# Actually update
skilz update

# Verify all up-to-date
skilz list --json | jq '.[] | select(.status != "up-to-date")'
```

### Scripting with JSON output

```bash
# Get all outdated skills
skilz list --json | jq -r '.[] | select(.status == "outdated") | .skill_id'

# Count installed skills
skilz list --json | jq length

# Export skill list
skilz list --json > installed-skills.json
```

### Cleaning up test installations

```bash
# Remove all project-level skills
for skill in $(skilz list --project --json | jq -r '.[].skill_name'); do
  skilz remove "$skill" --project --yes
done
```

---

## Development

Skilz uses [Task](https://taskfile.dev) for development automation.

### Prerequisites

- Python 3.10+
- [Task](https://taskfile.dev) (optional but recommended)

### Available Tasks

```bash
# Installation
task install          # Install in development mode

# Testing
task test             # Run all tests
task test:fast        # Run tests without verbose output
task coverage         # Run tests with coverage report
task coverage:html    # Generate HTML coverage report

# Code Quality
task lint             # Run linter (ruff)
task lint:fix         # Auto-fix linting issues
task format           # Format code with ruff
task typecheck        # Run type checker (mypy)
task check            # Run all quality checks

# Build & Release
task build            # Build distribution packages
task clean            # Remove build artifacts
task ci               # Run full CI pipeline locally

# Shortcuts
task t                # Alias for test
task c                # Alias for coverage
task l                # Alias for lint
task f                # Alias for format
```

### Manual Commands (without Task)

If you don't have Task installed, you can run commands directly:

```bash
PYTHONPATH=src python -m pytest tests/ -v              # Run tests
PYTHONPATH=src python -m pytest tests/ --cov=skilz     # Coverage
PYTHONPATH=src python -m skilz --version               # Test CLI
ruff check src/                                        # Lint
ruff format src/                                       # Format
mypy src/                                              # Type check
```

### Running Tests

```bash
# Run all tests
task test

# Run specific test file
PYTHONPATH=src python -m pytest tests/test_install_cmd.py -v

# Run with coverage
task coverage

# Run with coverage and show uncovered lines
task coverage:check
```

### Code Style

- **Linting**: Uses ruff for fast Python linting
- **Formatting**: Uses ruff format (compatible with Black)
- **Type checking**: Uses mypy for static type analysis
- **Coverage target**: 80% minimum (currently at 85%)

---

## Getting Help

```bash
# General help
skilz --help

# Command-specific help
skilz install --help
skilz list --help
skilz update --help
skilz remove --help
```

**Resources:**
- **Browse skills:** [skillzwave.ai](https://skillzwave.ai) — The largest agent and agent skills marketplace
- **Issues & Features:** [GitHub Repository](https://github.com/spillwave/skilz-cli)
- **Company:** [Spillwave](https://spillwave.com) — Leaders in agentic software development


# Complete walkthrough 
---

 % cat .skilz/registry.yaml           


spillwave/plantuml:
  git_repo: https://github.com/SpillwaveSolutions/plantuml.git
  skill_path: /main/SKILL.md
  git_sha: f2489dcd47799e4aaff3ae0a34cde0ebf2288a66

spillwave/design-doc-mermaid:
  git_repo: https://github.com/SpillwaveSolutions/design-doc-mermaid.git
  skill_path: /v1.0.0/SKILL.md
  git_sha: e1c29a38365c254c2fb0589e7bc1a11d23fc50a8

spillwave/notion-uploader-downloader:
  git_repo: https://github.com/SpillwaveSolutions/notion_uploader_downloader.git
  skill_path: /main/SKILL.md
  git_sha: ba6a3d7b25c4671bb72434b6d0fe6ac5ee8ae0c6

spillwave/document-specialist:
  git_repo: https://github.com/SpillwaveSolutions/document-specialist-skill.git
  skill_path: /main/SKILL.md
  git_sha: f917e99f386d4fab15d6d2f9afd70a8a5c04fe00

spillwave/sdd:
  git_repo: https://github.com/SpillwaveSolutions/sdd-skill.git
  skill_path: /main/SKILL.md
  git_sha: eba96064a34ae68c85c0a42186cf82da12ec5ef9

spillwave/gemini:
  git_repo: https://github.com/SpillwaveSolutions/gemini-skill.git
  skill_path: /main/SKILL.md
  git_sha: 0c99433da7c7cdb382c0436e50268796e9f307cf

spillwave/image-gen:
  git_repo: https://github.com/SpillwaveSolutions/image_gen.git
  skill_path: /main/SKILL.md
  git_sha: 2b8d0c4e33902e70def9d4ddf284b4519ad1023d

anthropics/algorithmic-art:
  git_repo: https://github.com/anthropics/skills.git
  skill_path: /main/skills/algorithmic-art/SKILL.md
  git_sha: 00756142ab04c82a447693cf373c4e0c554d1005

anthropics/brand-guidelines:
  git_repo: https://github.com/anthropics/skills.git
  skill_path: /main/skills/brand-guidelines/SKILL.md
  git_sha: 00756142ab04c82a447693cf373c4e0c554d1005

anthropics/canvas-design:
  git_repo: https://github.com/anthropics/skills.git
  skill_path: /main/skills/canvas-design/SKILL.md
  git_sha: 00756142ab04c82a447693cf373c4e0c554d1005
```

# Help
```
% skilz --help
usage: skilz [-h] [-V] [-v] {install,list,update,remove} ...

The universal package manager for AI skills.

positional arguments:
  {install,list,update,remove}
                        Available commands
    install             Install a skill from the registry
    list                List installed skills
    update              Update installed skills to latest versions
    remove              Remove an installed skill

options:
  -h, --help            show this help message and exit
  -V, --version         show program's version number and exit
  -v, --verbose         Enable verbose output

Examples:
  skilz install anthropics_skills/theme-factory
  skilz install some-skill --agent opencode
  skilz --version

```

# Install a skill to project
```
% skilz install anthropics_skills/algorithmic-art --project
Installed: anthropics_skills/algorithmic-art -> Claude Code (project)

% skilz list --project
Skill                               Version   Installed   Status
──────────────────────────────────────────────────────────────────
anthropics_skills/algorithmic-art   00756142  2025-12-15  up-to-date
anthropics_skills/brand-guidelines  00756142  2025-12-15  up-to-date
anthropics_skills/frontend-design   00756142  2025-12-14  up-to-date
anthropics_skills/theme-factory     e1c29a38  2025-12-14  up-to-date

% ls .claude/skills/algorithmic-art
LICENSE.txt	SKILL.md	templates

```

# Remove a skill from project

```

% skilz remove anthropics_skills/algorithmic-art --project
Remove anthropics_skills/algorithmic-art from Claude Code? [y/N] y
Removed: anthropics_skills/algorithmic-art

% ls .claude/skills/algorithmic-art
ls: .claude/skills/algorithmic-art: No such file or directory

% skilz list --project
Skill                               Version   Installed   Status
──────────────────────────────────────────────────────────────────
anthropics_skills/brand-guidelines  00756142  2025-12-15  up-to-date
anthropics_skills/frontend-design   00756142  2025-12-14  up-to-date
anthropics_skills/theme-factory     e1c29a38  2025-12-14  up-to-date

```




# Install a skill to user skills
```
% skilz install anthropics_skills/algorithmic-art
Installed: anthropics_skills/algorithmic-art -> Claude Code (user)

% skilz list
Skill                               Version   Installed   Status
──────────────────────────────────────────────────────────────────
anthropics_skills/algorithmic-art   00756142  2025-12-15  up-to-date

% ls  ~/.claude/skills/algorithmic-art
LICENSE.txt	SKILL.md	templates

```


# Remove a skill from user's skills

```

% skilz remove anthropics_skills/algorithmic-art
Remove anthropics_skills/algorithmic-art from Claude Code? [y/N] y
Removed: anthropics_skills/algorithmic-art

% ls ~/.claude/skills/algorithmic-art
ls: ~/.claude/skills/algorithmic-art: No such file or directory

% skilz list
No skills installed.

```




# Install a skill to user's skills for different agents
```bash
# OpenCode CLI
skilz install anthropics_skills/algorithmic-art --agent opencode
skilz list --agent opencode
ls ~/.config/opencode/skill/algorithmic-art

# Gemini CLI
skilz install anthropics_skills/algorithmic-art --agent gemini
skilz list --agent gemini
ls ~/.gemini/skills/algorithmic-art

# OpenHands
skilz install anthropics_skills/algorithmic-art --agent openhands
skilz list --agent openhands
ls ~/.openhands/skills/algorithmic-art
```

# Remove a skill from user's skills

```bash
skilz remove anthropics_skills/algorithmic-art --agent opencode
skilz remove anthropics_skills/algorithmic-art --agent gemini
skilz remove anthropics_skills/algorithmic-art --agent openhands
ls  ~/.config/opencode/skills/algorithmic-art
skilz list --agent opencode
```
