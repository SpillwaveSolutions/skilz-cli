# Skilz

**The universal package manager for AI skills.**

[![PyPI version](https://badge.fury.io/py/skilz.svg)](https://pypi.org/project/skilz/)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Skilz installs and manages AI skills (agents and tools) across multiple AI coding assistants. Think `npm install` or `pip install`, but for skills.

Skilz follows the [agentskills.io](https://agentskills.io/) standard and supports the [AGENTS.md](https://agents.md/) ecosystem.

**Built by [Spillwave](https://spillwave.com)** — Leaders in agentic software development.

**Browse skills at [Skillzwave.ai](https://skillzwave.ai)** — The largest agent and agent skills marketplace.

---

## Why Skilz?

Today, installing AI skills requires manual file copying, marketplace browsing, or plugin commands that vary by tool. Skilz unifies this experience:

- **One command** installs any skill from any Git repository
- **Works everywhere** — Claude Code, OpenCode, and more coming
- **Reproducible** — pin skills to specific commits for consistent behavior
- **Auditable** — manifest files track what's installed and where it came from

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

### Development Setup

```bash
git clone https://github.com/spillwave/skilz-cli.git
cd skilz-cli
pip install -e ".[dev]"
```

For detailed usage instructions, see the [User Manual](docs/USER_MANUAL.md).

---

## Quick Start

```bash
# Install a skill from the marketplace using NEW format (defaults to Claude Code, user-level)
skilz install anthropics/skills/algorithmic-art

# Install using LEGACY format (backwards compatible)
skilz install anthropics_skills/algorithmic-art

# Install directly from GitHub URL (NEW in 1.5 - no -g flag needed)
skilz install https://github.com/owner/repo

# Install for a specific agent using NEW format
skilz install anthropics/skills/brand-guidelines --agent opencode

# Install at project level (for sandboxed agents)
skilz install anthropics/skills/frontend-design --agent copilot -p

# Gemini CLI native support (NEW in 1.7 - requires experimental.skills plugin)
skilz install anthropics/skills/pdf-reader --agent gemini --project

# Legacy Gemini workflow (NEW in 1.7 - for users without experimental.skills)
skilz install anthropics/skills/pdf-reader --agent universal --project --config GEMINI.md

# Universal agent with custom config (NEW in 1.7)
skilz install anthropics/skills/excel --agent universal --project --config CUSTOM.md

# List installed skills (or use alias: skilz ls)
skilz list

# Search for skills on GitHub (NEW in 1.5)
skilz search excel
skilz search pdf --limit 5

# Visit a skill's GitHub page (NEW in 1.5)
skilz visit anthropics/skills

# Read skill content (for agents without native skill loading)
skilz read algorithmic-art

# Update all skills to latest registry versions
skilz update

# Uninstall a skill (or use alias: skilz rm)
skilz uninstall anthropics/skills/algorithmic-art
```

### Skill ID Formats

Skilz supports two skill ID formats:

- **NEW Format (Recommended)**: `owner/repo/skill-name` — e.g., `anthropics/skills/theme-factory`
- **LEGACY Format**: `owner_repo/skill-name` — e.g., `anthropics_skills/theme-factory`

Both formats work identically. Use whichever you prefer!

Each install command:

1. Resolves the skill from the registry
2. Clones the repository (or reuses an existing clone)
3. Checks out the pinned commit
4. Copies the skill to the appropriate location
5. Writes a manifest for tracking

---

## User Journey

1. Browse skills at **[skillzwave.ai](https://skillzwave.ai)**
2. Copy the install command from the skill page
3. Run it locally

**Example:**

The skill page for [Theme Factory](https://skillzwave.ai/skill/anthropics_skills/theme-factory/) shows:

```bash
skilz install anthropics_skills/theme-factory
```

The string `anthropics_skills/theme-factory` is the **Skill ID**. Skilz supports two formats:

- **NEW Format (Recommended)**: `owner/repo/skill-name` — e.g., `anthropics/skills/theme-factory`
- **LEGACY Format**: `owner_repo/skill-name` — e.g., `anthropics_skills/theme-factory` (underscores separate owner and repo)

Both formats work identically and resolve to the same skill. The NEW format is more intuitive and matches GitHub repository structure.

---

## How It Works

Skilz reads from a registry file that maps Skill IDs to their Git locations:

| Location | Scope |
|----------|-------|
| `.skilz/registry.yaml` | Project-level |
| `~/.skilz/registry.yaml` | User-level |

The registry tells Skilz exactly where to find each skill and which version to install.

---

## Agent Installation Modes (NEW in 1.7)

Skilz supports different installation modes depending on the AI agent:

### Native Agent Support

Agents with **native skill support** read skills directly from their designated directories:

- **Claude Code**: `.claude/skills/` → No config file needed
- **OpenCode**: `.opencode/skill/` → No config file needed  
- **Codex**: `.codex/skills/` → No config file needed
- **GitHub Copilot**: `.github/skills/` → No config file needed
- **Gemini CLI** (NEW in 1.7): `.gemini/skills/` → Requires `experimental.skills` plugin

**Example:**
```bash
# Install for Gemini with native support (requires experimental.skills plugin)
skilz install pdf-reader --agent gemini --project
# → Installs to: .gemini/skills/pdf-reader/
# → Config file: None (Gemini reads directory natively)
```

### Legacy/Universal Mode

For agents without native support or legacy workflows, use the **universal agent** with custom config files:

**Example:**
```bash
# Legacy Gemini workflow (for users without experimental.skills plugin)
skilz install pdf-reader --agent universal --project --config GEMINI.md
# → Installs to: .skilz/skills/pdf-reader/
# → Config file: GEMINI.md (created/updated with skill reference)
```

**Custom Config Example:**
```bash
# Use any custom config file name
skilz install excel --agent universal --project --config MY_SKILLS.md
# → Installs to: .skilz/skills/excel/
# → Config file: MY_SKILLS.md (created/updated)
```

### When to Use Which Mode

| Scenario | Command | Result |
|----------|---------|--------|
| Gemini with plugin | `--agent gemini --project` | Native: `.gemini/skills/` |
| Gemini without plugin | `--agent universal --project --config GEMINI.md` | Universal: `.skilz/skills/` + GEMINI.md |
| Claude Code | `--agent claude` | Native: `~/.claude/skills/` |
| Multi-agent project | `--agent universal --project` | Universal: `.skilz/skills/` + AGENTS.md |
| Custom workflow | `--agent universal --project --config CUSTOM.md` | Universal: `.skilz/skills/` + CUSTOM.md |

For detailed migration guides, see:
- [Gemini Migration Guide](docs/GEMINI_MIGRATION.md)
- [Universal Agent Guide](docs/UNIVERSAL_AGENT_GUIDE.md)

---

## CLI Reference

### `skilz install <skill-id>`

Install a skill from the registry or marketplace.

```bash
skilz install anthropics_skills/theme-factory           # Auto-detect agent
skilz install anthropics_skills/theme-factory --agent claude
skilz install anthropics_skills/theme-factory --agent opencode
skilz install anthropics_skills/theme-factory --project # Project-level
```

### `skilz list`

Show all installed skills with their versions and status.

```bash
skilz list                   # All user-level skills
skilz list --project         # Project-level skills
skilz list --agent claude    # Only Claude Code skills
skilz list --json            # Output as JSON
```

**Output example:**
```
Skill                               Version   Installed   Status
────────────────────────────────────────────────────────────────────────
anthropics_skills/algorithmic-art   00756142  2025-01-15  up-to-date
anthropics_skills/theme-factory     f2489dcd  2025-01-15  outdated
```

### `skilz update [skill-id]`

Update installed skills to match registry versions.

```bash
skilz update                                    # Update all skills
skilz update anthropics_skills/algorithmic-art  # Update specific skill
skilz update --dry-run                          # Show what would be updated
skilz update --project                          # Update project-level skills
```

### `skilz uninstall <skill-id>` (alias: `rm`)

Uninstall an installed skill.

```bash
skilz uninstall anthropics_skills/theme-factory    # Prompts for confirmation
skilz uninstall anthropics_skills/theme-factory -y # Skip confirmation
skilz rm theme-factory --project                   # Remove by name (using alias)
```

### `skilz search <query>` (NEW in 1.5)

Search GitHub for available skills.

```bash
skilz search excel              # Search for excel-related skills
skilz search pdf --limit 5      # Limit to 5 results
skilz search "data" --json      # JSON output for scripting
```

### `skilz visit <source>` (NEW in 1.5)

Open a skill's GitHub page in your default browser.

```bash
skilz visit anthropics/skills          # Opens repo page
skilz visit anthropics/skills/excel    # Opens skill directory
skilz visit https://github.com/...     # Opens full URL
```

### Command Aliases

For Unix-like familiarity:

| Original | Alias |
|----------|-------|
| `skilz list` | `skilz ls` |
| `skilz uninstall` | `skilz rm` |

For complete documentation including troubleshooting and advanced examples, see the [User Manual](docs/USER_MANUAL.md).

---

## Supported Agents

Skilz supports **30+ AI coding agents** from the [AGENTS.md](https://agents.md/) ecosystem, including Claude Code, OpenAI Codex, Gemini CLI, GitHub Copilot, Cursor, Aider, Windsurf, Zed AI, RooCode, Devin, Google Antigravity, Qwen Code, OpenHands, Cline, Goose, and many more.

### Skill Support Levels

| Level | Description | Example Agents |
|-------|-------------|----------------|
| **Full Support** | Native skill directories at user or project level | Claude Code, OpenCode, Codex |
| **Project Support** | Project-level installation via `--project` | Cursor, Aider, Gemini CLI |
| **Universal** | Any AGENTS.md-compatible agent via `--agent universal` | Ona, Amp, Devin, Factory, Jules |

### Full Skill Support (Native Directories)

Agents with dedicated skill directories - skills install to user or project level.

| Agent | User-Level | Project-Level | Notes |
|-------|------------|---------------|-------|
| Gemini CLI | `~/.gemini/skills/` | `.gemini/skills/` | Uses GEMINI.md |
| OpenCode CLI | `~/.config/opencode/skill/` | `.opencode/skill/` | Reads AGENTS.md (singular path) |
| OpenHands | `~/.openhands/skills/` | `.openhands/skills/` | Reads AGENTS.md |
| Claude Code | `~/.claude/skills/` | `.claude/skills/` | Uses CLAUDE.md (not AGENTS.md) |
| Cline | `~/.cline/skills/` | `.cline/skills/` | Reads AGENTS.md |
| OpenAI Codex | `~/.codex/skills/` | `.codex/skills/` | Reads AGENTS.md |
| Cursor | `~/.cursor/skills/` | `.cursor/skills/` | Native support (updated) |
| Goose | `~/.config/goose/skills/` | `.goose/skills/` | Reads AGENTS.md |
| Roo Code | `~/.roo/skills/` | `.roo/skills/` | Reads AGENTS.md |
| Kilo Code | `~/.kilocode/skills/` | `.kilocode/skills/` | Reads AGENTS.md |
| Trae | `~/.trae/skills/` | `.trae/skills/` | Reads AGENTS.md |
| Droid | `~/.factory/skills/` | `.factory/skills/` | Reads AGENTS.md |
| Clawdbot | `~/.clawdbot/skills/` | `skills/` | Unique project path |
| Kiro CLI | `~/.kiro/skills/` | `.kiro/skills/` | Reads AGENTS.md |
| Pi | `~/.pi/agent/skills/` | `.pi/skills/` | Reads AGENTS.md |
| Neovate | `~/.neovate/skills/` | `.neovate/skills/` | Reads AGENTS.md |
| Antigravity | `~/.gemini/antigravity/skills/` | `.agent/skills/` | Native discovery |
| Windsurf | `~/.codeium/windsurf/skills/` | `.windsurf/skills/` | Native support (updated) |
| GitHub Copilot | `~/.copilot/skills/` | `.github/skills/` | Native support (updated) |
| Qwen Code | `~/.qwen/skills/` | `.qwen/skills/` | Uses QWEN.md |
| Zencoder | `~/.zencoder/skills/` | `.zencoder/skills/` | Reads AGENTS.md |
| Amp | `~/.config/agents/skills/` | `.agents/skills/` | Reads AGENTS.md |
| Qoder | `~/.qoder/skills/` | `.qoder/skills/` | Reads AGENTS.md |
| Command Code | `~/.commandcode/skills/` | `.commandcode/skills/` | Reads AGENTS.md |

### Bridged Support (via .skilz/skills/)

Agents that use the universal `.skilz/skills/` directory with config injection.

| Agent | Project-Level | Config File | Notes |
|-------|---------------|-------------|-------|
| Aider | `.skilz/skills/` | `CONVENTIONS.md` | CLI-first agent |
| Zed AI | `.skilz/skills/` | `AGENTS.md` | High-performance editor |
| Crush | `.skilz/skills/` | `AGENTS.md` | - |
| Kimi CLI | `.skilz/skills/` | `AGENTS.md` | Moonshot AI |
| Plandex | `.skilz/skills/` | `AGENTS.md` | - |
| Universal | `.skilz/skills/` | `AGENTS.md` | Fallback for any agent |

### Universal Support (AGENTS.md Compatible)

Any agent can use universal mode via `--agent universal --project`:

| Agent | Provider | Installation Command |
|-------|----------|---------------------|
| Ona | - | `skilz install skill --agent universal --project` |
| Devin | Cognition | `skilz install skill --agent universal --project` |
| Factory | Factory | `skilz install skill --agent universal --project` |
| Jules | Google | `skilz install skill --agent universal --project` |
| Phoenix | - | `skilz install skill --agent universal --project` |
| Warp | Warp | `skilz install skill --agent universal --project` |
| VS Code | Microsoft | `skilz install skill --agent universal --project` |
| Semgrep | Semgrep | `skilz install skill --agent universal --project` |
| Autopilot | UiPath | `skilz install skill --agent universal --project` |

**Note:** Universal support works with any agent that reads the AGENTS.md config file format. Skills are installed to `.skilz/skills/` and referenced in the project's AGENTS.md file.

For detailed agent-specific instructions, see the [Supported Agents Guide](docs/SUPPORTED_AGENTS.md) and [Comprehensive User Guide](docs/COMPREHENSIVE_USER_GUIDE.md)

---

## Registry Format

The registry is a YAML file mapping Skill IDs to their source locations.

### Phase 1: Direct Git Installation

```yaml
# .skilz/registry.yaml

anthropics_skills/algorithmic-art:
  git_repo: https://github.com/anthropics/skills.git
  skill_path: /main/skills/algorithmic-art/SKILL.md
  git_sha: ee131b98d0e39c27b5e69ba84603b49254b0119d

anthropics_skills/theme-factory:
  git_repo: https://github.com/anthropics/skills.git
  skill_path: /main/skills/theme-factory/SKILL.md
  git_sha: ee131b98d0e39c27b5e69ba84603b49254b0119d

my-company/internal-skill:
  git_repo: git@github.com:my-company/ai-skills.git
  skill_path: /main/skills/internal-skill/SKILL.md
  git_sha: a1b2c3d4e5f6789012345678901234567890abcd
```

### Phase 2: Plugin and Marketplace Installation

Phase 2 extends the registry to support plugin-based installs:

```yaml
# .skilz/registry.yaml

anthropics_skills/frontend-design:
  git_repo: https://github.com/anthropics/skills.git
  skill_path: skills/frontend-design
  git_sha: ee131b98d0e39c27b5e69ba84603b49254b0119d
  plugin: true
  marketplace_path: /main/.claude-plugin/marketplace.json
  plugin_id: frontend-design
```

---

## Registry Schema Reference

### Phase 1 Schema

Each registry entry must include these fields:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `git_repo` | string | Yes | Git repository URL (SSH or HTTPS) |
| `skill_path` | string | Yes | Path to the skill within the repository, including branch or tag |
| `git_sha` | string | Yes | Full 40-character Git commit SHA for reproducibility |

**JSON Schema (Phase 1):**

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "$id": "https://skillzwave.ai/schemas/registry-entry-v1.json",
  "title": "Skilz Registry Entry (Phase 1)",
  "description": "Schema for a skill registry entry supporting direct Git installation",
  "type": "object",
  "required": ["git_repo", "skill_path", "git_sha"],
  "additionalProperties": false,
  "properties": {
    "git_repo": {
      "type": "string",
      "description": "Git repository URL (SSH or HTTPS format)",
      "examples": [
        "git@github.com:anthropics/skills.git",
        "https://github.com/anthropics/skills.git"
      ]
    },
    "skill_path": {
      "type": "string",
      "description": "Path to the skill directory or SKILL.md file within the repository. May include branch or tag prefix.",
      "pattern": "^/.*",
      "examples": [
        "/main/skills/web-artifacts-builder/SKILL.md",
        "/v1.2.0/skills/document-generator/SKILL.md"
      ]
    },
    "git_sha": {
      "type": "string",
      "description": "Full 40-character Git commit SHA",
      "pattern": "^[a-f0-9]{40}$",
      "examples": ["ee131b98d0e39c27b5e69ba84603b49254b0119d"]
    }
  }
}
```

### Phase 2 Schema

Phase 2 adds optional fields for plugin-based installation:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `git_repo` | string | Yes | Git repository URL (SSH or HTTPS) |
| `skill_path` | string | Yes | Path to the skill within the repository |
| `git_sha` | string | Yes | Full 40-character Git commit SHA |
| `plugin` | boolean | No | If `true`, install via plugin mechanism |
| `marketplace_path` | string | Conditional | Path to `marketplace.json`. Required if `plugin: true` |
| `plugin_id` | string | Conditional | Plugin identifier. Required if `plugin: true` |

**JSON Schema (Phase 2):**

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "$id": "https://skillzwave.ai/schemas/registry-entry-v2.json",
  "title": "Skilz Registry Entry (Phase 2)",
  "description": "Schema for a skill registry entry supporting both direct Git and plugin-based installation",
  "type": "object",
  "required": ["git_repo", "skill_path", "git_sha"],
  "additionalProperties": false,
  "properties": {
    "git_repo": {
      "type": "string",
      "description": "Git repository URL (SSH or HTTPS format)",
      "examples": [
        "git@github.com:anthropics/skills.git",
        "https://github.com/anthropics/skills.git"
      ]
    },
    "skill_path": {
      "type": "string",
      "description": "Path to the skill directory or SKILL.md file. For plugin installs, this is relative to the plugin root.",
      "examples": [
        "/main/skills/web-artifacts-builder/SKILL.md",
        "skills/marketplace-skill"
      ]
    },
    "git_sha": {
      "type": "string",
      "description": "Full 40-character Git commit SHA",
      "pattern": "^[a-f0-9]{40}$",
      "examples": ["ee131b98d0e39c27b5e69ba84603b49254b0119d"]
    },
    "plugin": {
      "type": "boolean",
      "default": false,
      "description": "If true, install using the plugin/marketplace mechanism"
    },
    "marketplace_path": {
      "type": "string",
      "description": "Path to the marketplace.json file within the repository. Required when plugin is true.",
      "examples": ["/main/.claude-plugin/marketplace.json"]
    },
    "plugin_id": {
      "type": "string",
      "description": "Identifier for the plugin within the marketplace. Required when plugin is true.",
      "examples": ["web-artifacts-builder", "document-skills"]
    }
  },
  "if": {
    "properties": { "plugin": { "const": true } },
    "required": ["plugin"]
  },
  "then": {
    "required": ["marketplace_path", "plugin_id"]
  }
}
```

---

## Manifest Files

When Skilz installs a skill, it writes a `.skilz-manifest.yaml` file into the skill directory:

```yaml
installed_at: 2025-01-15T14:32:00Z
skill_id: anthropics_skills/theme-factory
git_repo: https://github.com/anthropics/skills.git
skill_path: /main/skills/theme-factory/SKILL.md
git_sha: ee131b98d0e39c27b5e69ba84603b49254b0119d
skilz_version: 0.1.0
```

This enables:

- **Auditing** — know exactly what's installed and where it came from
- **Upgrade detection** — compare installed SHA against registry
- **Troubleshooting** — trace issues back to specific commits

---

## Comparison with Native Installation

| Method | Skilz | Claude Plugin System | Manual Copy |
|--------|-------|---------------------|-------------|
| Single command install | ✓ | ✓ | ✗ |
| Any Git repository | ✓ | Marketplace only | ✓ |
| Private repositories | ✓ | ✗ | ✓ |
| Version pinning | ✓ | ✗ | Manual |
| Install manifest | ✓ | ✗ | ✗ |
| Cross-agent support | ✓ (22+ agents) | ✗ | ✗ |
| Symlink mode | ✓ | ✗ | ✓ |

---

## Roadmap

### Phase 1-3 - Core Installer (Complete)

- [x] Registry-based skill resolution
- [x] Direct Git installation
- [x] Claude Code support
- [x] OpenCode support
- [x] Manifest file generation
- [x] `skilz list` — show installed skills with status
- [x] `skilz update` — update skills to latest pinned SHA
- [x] `skilz remove` — uninstall a skill
- [x] 85%+ test coverage (448 tests)
- [x] Taskfile automation
- [x] Documentation updates

### Phase 4-5 - Distribution (Complete)

- [x] PyPI publishing (`pip install skilz`)
- [x] Local skill installation (`skilz install -f /path/to/skill`)

### Phase 6-7 - Multi-Agent Support (Complete)

- [x] 22+ AI agent support via AGENTS.md ecosystem
- [x] Universal skills directory (`~/.skilz/skills/`)
- [x] Copy vs symlink installation modes
- [x] Config file sync (agentskills.io standard)
- [x] `skilz read` command for agents without native skill loading
- [x] Comprehensive User Guide

### Phase 8 - Discovery & UX (Complete)

- [x] `skilz search` command for GitHub skill discovery
- [x] `skilz visit` command to open skill pages in browser
- [x] Command aliases (`ls`, `rm`)
- [x] URL auto-detection for `skilz install`
- [x] Native agent optimization (skip config sync)
- [x] `--force-config` flag

### Future

- [ ] Plugin and marketplace installation support
- [ ] `skilz search` integration with [skillzwave.ai](https://skillzwave.ai)
- [ ] Skill dependency resolution

---

## Alternative Installation Methods (Claude Native)

For reference, Claude Code supports these native installation methods:

**Manual file copy:**
```bash
git clone https://github.com/anthropics/skills.git
cp -r skills/web-artifacts-builder ~/.claude/skills/
```

**Plugin marketplace:**
```
/plugin marketplace add anthropics/skills
/plugin install web-artifacts-builder
```

**Local directory:**
```
/plugin add /path/to/skill-directory
```

Skilz complements these methods by providing reproducible, cross-environment installs from any Git source.

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

# E2E Testing
./scripts/end_to_end.sh                    # Full E2E test suite
./scripts/test_rest_marketplace_e2e.sh     # Live API testing
./scripts/test_api_integration.sh          # API integration tests
./scripts/test_bug_fixes_e2e.sh            # Bug fix regression tests

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

```bash
PYTHONPATH=src python -m pytest tests/ -v              # Run tests
PYTHONPATH=src python -m pytest tests/ --cov=skilz     # Coverage
PYTHONPATH=src python -m skilz --version               # Test CLI
```

---

## Related Projects

- [Skillzwave.ai](https://skillzwave.ai) — The largest agent and agent skills marketplace
- [Spillwave](https://spillwave.com) — Leaders in agentic software development
- [OpenSkills](https://github.com/numman-ali/openskills) — Open-source skill format standardization
- [Anthropic Skills](https://github.com/anthropics/skills) — Official Anthropic skills repository

---

## Vision

**Skilz brings skills to all AI agents via the [AGENTS.md](https://agents.md/) standard.**

Skilz follows the [agentskills.io](https://agentskills.io/) standard for skill format and supports the full AGENTS.md ecosystem of 22+ coding agents.

For Claude Code users:
- Install skills from any GitHub repository
- Use private repos and local paths
- Share skills across multiple agents
- Version-control skills in your own repositories

For other agents:
- Universal access to Claude's skills ecosystem via AGENTS.md
- Use Anthropic marketplace skills via GitHub
- Progressive disclosure — load skills on demand

**Get started:** Browse available skills at [skillzwave.ai](https://skillzwave.ai) and install with a single command.

---
