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

```bash
pip install skilz
```

---

## Quick Start

```bash
# Install a skill
skilz install anthropics/web-artifacts-builder

# Install more skills
skilz install seo-master
skilz install legal-reviewer
skilz install salesforce-connector
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

The skill page for [Web Artifacts Builder](https://skillzwave.ai/skill/anthropics__skills__web-artifacts-builder__SKILL/) shows:

```bash
skilz install anthropics/web-artifacts-builder
```

The string `anthropics/web-artifacts-builder` is the **Skill ID** — an opaque identifier that may contain `/` characters.

---

## How It Works

Skilz reads from a registry file that maps Skill IDs to their Git locations:

| Location | Scope |
|----------|-------|
| `.skilz/registry.yaml` | Project-level |
| `~/.skilz/registry.yaml` | User-level |

The registry tells Skilz exactly where to find each skill and which version to install.

---

## Supported Environments

Skilz auto-detects and installs skills into:

| Environment | Skills Directory |
|-------------|------------------|
| Claude Code | `~/.claude/skills/` (personal) or `.claude/skills/` (project) |
| OpenCode | `~/.config/opencode/skills/` |

---

## Registry Format

The registry is a YAML file mapping Skill IDs to their source locations.

### Phase 1: Direct Git Installation

```yaml
# .skilz/registry.yaml

anthropics/web-artifacts-builder:
  git_repo: git@github.com:anthropics/skills.git
  skill_path: /main/skills/web-artifacts-builder/SKILL.md
  git_sha: ee131b98d0e39c27b5e69ba84603b49254b0119d

anthropics/document-generator:
  git_repo: git@github.com:anthropics/skills.git
  skill_path: /main/skills/document-generator/SKILL.md
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

some-org/marketplace-skill:
  git_repo: git@github.com:some-org/skills-repo.git
  skill_path: skills/marketplace-skill
  git_sha: ee131b98d0e39c27b5e69ba84603b49254b0119d
  plugin: true
  marketplace_path: /main/.claude-plugin/marketplace.json
  plugin_id: marketplace-skill
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
skill_id: anthropics/web-artifacts-builder
git_repo: git@github.com:anthropics/skills.git
skill_path: /main/skills/web-artifacts-builder/SKILL.md
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
| Cross-agent support | ✓ | ✗ | ✗ |
| Local development (symlinks) | Planned | ✗ | ✓ |

---

## Roadmap

### Phase 1 (Current)

- [x] Registry-based skill resolution
- [x] Direct Git installation
- [x] Claude Code support
- [x] OpenCode support
- [x] Manifest file generation
- [ ] `skilz list` — show installed skills
- [ ] `skilz update` — update skills to latest pinned SHA
- [ ] `skilz remove` — uninstall a skill

### Phase 2

- [ ] Plugin and marketplace installation support
- [ ] Extended registry format
- [ ] `skilz search` — search skillzwave.ai from CLI

### Future

- [ ] Cursor support
- [ ] Codex support
- [ ] Gemini support (proof of concept complete)
- [ ] Symlink mode for local development
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
