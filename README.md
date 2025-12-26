# Skilz

**The universal package manager for AI skills.**

Skilz installs and manages AI skills (agents and tools) across multiple AI coding assistants. Think `npm install` or `pip install`, but for skills.

---

## Why Skilz?

Today, installing AI skills requires manual file copying, marketplace browsing, or plugin commands that vary by tool. Skilz unifies this experience:

- **One command** installs any skill from any Git repository
- **Works everywhere** — Claude Code, OpenCode, and more coming
- **Reproducible** — pin skills to specific commits for consistent behavior
- **Auditable** — manifest files track what's installed and where it came from

---

## Installation

### From GitHub (recommended until PyPI release)

```bash
# Install directly from GitHub
pip install git+https://github.com/spillwave/skilz-cli.git

# Or clone and install
git clone https://github.com/spillwave/skilz-cli.git
cd skilz-cli
pip install .
```

### From PyPI (coming soon)

```bash
# Not yet available - will be:
pip install skilz
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
# Install a skill from the marketplace (defaults to Claude Code, user-level)
skilz install anthropics_skills/algorithmic-art

# Install for a specific agent
skilz install anthropics_skills/brand-guidelines --agent gemini

# Install at project level (for sandboxed agents)
skilz install anthropics_skills/frontend-design --agent copilot --project

# List installed skills
skilz list

# Read skill content (for agents without native skill loading)
skilz read algorithmic-art

# Update all skills to latest registry versions
skilz update

# Remove a skill
skilz remove anthropics_skills/algorithmic-art
```

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

The string `anthropics_skills/theme-factory` is the **Skill ID** — the format is `owner_repo/skill-name` where underscores separate owner and repo.

---

## How It Works

Skilz reads from a registry file that maps Skill IDs to their Git locations:

| Location | Scope |
|----------|-------|
| `.skilz/registry.yaml` | Project-level |
| `~/.skilz/registry.yaml` | User-level |

The registry tells Skilz exactly where to find each skill and which version to install.

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

### `skilz remove <skill-id>`

Remove an installed skill.

```bash
skilz remove anthropics_skills/theme-factory    # Prompts for confirmation
skilz remove anthropics_skills/theme-factory -y # Skip confirmation
skilz remove theme-factory --project            # Remove by name
```

For complete documentation including troubleshooting and advanced examples, see the [User Manual](docs/USER_MANUAL.md).

---

## Supported Agents

Skilz supports 14 AI coding assistants:

| Agent | User-Level | Project-Level | Default Mode |
|-------|------------|---------------|--------------|
| Claude Code | `~/.claude/skills/` | `.claude/skills/` | copy |
| OpenAI Codex | `~/.codex/skills/` | `.codex/skills/` | copy |
| OpenCode CLI | `~/.config/opencode/skills/` | `.skilz/skills/` | copy |
| Universal | `~/.skilz/skills/` | `.skilz/skills/` | copy |
| Gemini CLI | - | `.skilz/skills/` | copy |
| GitHub Copilot | - | `.github/copilot/skills/` | copy |
| Cursor | - | `.skills/skills/` | copy |
| Aider | - | `.skills/skills/` | copy |
| Windsurf | - | `.skills/skills/` | copy |
| Qwen CLI | - | `.skills/skills/` | copy |
| Kimi CLI | - | `.skills/skills/` | copy |
| Crush | - | `.skills/skills/` | copy |
| Plandex | - | `.skills/skills/` | copy |
| Zed AI | - | `.skills/skills/` | copy |

For detailed agent-specific instructions, see the [Comprehensive User Guide](docs/COMPREHENSIVE_USER_GUIDE.md)

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
| Cross-agent support | ✓ (14 agents) | ✗ | ✗ |
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
- [x] 92% test coverage (418 tests)
- [x] Taskfile automation
- [x] Documentation updates

### Phase 6-7 - Multi-Agent Support (Complete)

- [x] 14 AI agent support (Claude, Codex, Gemini, Copilot, Cursor, Aider, etc.)
- [x] Universal skills directory (`~/.skilz/skills/`)
- [x] Copy vs symlink installation modes
- [x] Config file sync (agentskills.io standard)
- [x] `skilz read` command for agents without native skill loading
- [x] Comprehensive User Guide

### Future

- [ ] PyPI publishing
- [ ] Plugin and marketplace installation support
- [ ] `skilz search` — search skillzwave.ai from CLI
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

- [OpenSkills](https://github.com/numman-ali/openskills) — Open-source skill format standardization
- [Anthropic Skills](https://github.com/anthropics/skills) — Official Anthropic skills repository

---

## Vision

**Skilz brings Anthropic's skills system to all AI agents.**

For Claude Code users:
- Install skills from any GitHub repository
- Use private repos and local paths
- Share skills across multiple agents
- Version-control skills in your own repositories

For other agents:
- Universal access to Claude's skills ecosystem
- Use Anthropic marketplace skills via GitHub
- Progressive disclosure — load skills on demand

---
