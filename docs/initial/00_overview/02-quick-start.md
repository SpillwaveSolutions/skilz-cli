# Quick Start Guide

**Browse skills:** [skillzwave.ai](https://skillzwave.ai) — The largest agent and agent skills marketplace
**Built by:** [Spillwave](https://spillwave.com) — Leaders in agentic software development

## Installation

### Using pip (Recommended)

```bash
pip install skilz
```

### From Source

```bash
# Clone the repository
git clone https://github.com/spillwave/skilz-cli
cd skilz-cli

# Install in development mode
pip install -e ".[dev]"

# Or using Task
task install
```

### Verify Installation

```bash
skilz --version
# Output: skilz 1.2.0
```

## Basic Usage

### 1. Install a Skill

Install a skill from the registry:

```bash
skilz install anthropics/web-artifacts-builder
```

**Output:**
```
Auto-detected agent: Claude Code
Looking up skill: anthropics/web-artifacts-builder
Fetching repository...
Checking out a1b2c3d4...
Installing to /Users/you/.claude/skills/web-artifacts-builder...
Installed: anthropics/web-artifacts-builder -> Claude Code (user)
```

### 2. List Installed Skills

View all installed skills:

```bash
skilz list
```

**Output:**
```
Skill                                 Version    Installed    Status
──────────────────────────────────────────────────────────────────────────
anthropics/web-artifacts-builder      a1b2c3d4   2025-12-14   up-to-date
spillwave/plantuml                    b2c3d4e5   2025-12-13   outdated
```

### 3. Update Skills

Update all outdated skills:

```bash
skilz update
```

**Output:**
```
Checking 2 installed skill(s)...
  anthropics/web-artifacts-builder: up-to-date (a1b2c3d4)
  spillwave/plantuml: updating b2c3d4e5 -> c3d4e5f6
Updated: spillwave/plantuml -> Claude Code (user)

Updated 1 skill(s), 1 already up-to-date
```

Update a specific skill:

```bash
skilz update spillwave/plantuml
```

### 4. Remove a Skill

Remove an installed skill:

```bash
skilz remove web-artifacts-builder
```

**Output:**
```
Remove anthropics/web-artifacts-builder from Claude Code? [y/N] y
Removed: anthropics/web-artifacts-builder
```

Skip confirmation:

```bash
skilz remove web-artifacts-builder -y
```

## Command Reference

### Install Command

```bash
skilz install <skill_id> [--agent <agent>] [--project]
```

**Arguments:**
- `skill_id`: Skill identifier from registry (e.g., `anthropics/web-artifacts-builder`)

**Options:**
- `--agent <agent>`: Target agent (`claude` or `opencode`), auto-detected if not specified
- `--project`: Install to project directory (`.claude/skills`) instead of user directory
- `-v, --verbose`: Show detailed progress information

**Examples:**

```bash
# Basic install
skilz install anthropics/web-artifacts-builder

# Install to OpenCode
skilz install some-skill --agent opencode

# Install to project directory
skilz install my-skill --project

# Verbose output
skilz install -v anthropics/web-artifacts-builder
```

### List Command

```bash
skilz list [--agent <agent>] [--project] [--json]
```

**Options:**
- `--agent <agent>`: Filter by agent type
- `--project`: List project-level skills instead of user-level
- `--json`: Output as JSON
- `-v, --verbose`: Show debug information

**Examples:**

```bash
# List all user-level skills
skilz list

# List project-level skills
skilz list --project

# List only Claude Code skills
skilz list --agent claude

# JSON output
skilz list --json
```

**JSON Output Format:**

```json
[
  {
    "skill_id": "anthropics/web-artifacts-builder",
    "skill_name": "web-artifacts-builder",
    "git_sha": "a1b2c3d4e5f6789012345678901234567890abcd",
    "installed_at": "2025-12-14T20:00:00+00:00",
    "status": "up-to-date",
    "path": "/Users/you/.claude/skills/web-artifacts-builder",
    "agent": "claude",
    "project_level": false
  }
]
```

### Update Command

```bash
skilz update [skill_id] [--agent <agent>] [--project] [--dry-run]
```

**Arguments:**
- `skill_id`: (Optional) Specific skill to update. Updates all if omitted.

**Options:**
- `--agent <agent>`: Filter by agent type
- `--project`: Update project-level skills
- `--dry-run`: Show what would be updated without making changes
- `-v, --verbose`: Show detailed progress

**Examples:**

```bash
# Update all skills
skilz update

# Update specific skill
skilz update anthropics/web-artifacts-builder

# Dry run to see what would change
skilz update --dry-run

# Update only Claude Code skills
skilz update --agent claude
```

### Remove Command

```bash
skilz remove <skill_id> [--agent <agent>] [--project] [-y]
```

**Arguments:**
- `skill_id`: Skill to remove (ID or name)

**Options:**
- `--agent <agent>`: Filter by agent type
- `--project`: Remove project-level skill
- `-y, --yes`: Skip confirmation prompt
- `-v, --verbose`: Show detailed progress

**Examples:**

```bash
# Remove with confirmation
skilz remove web-artifacts-builder

# Remove without confirmation
skilz remove web-artifacts-builder -y

# Remove by full ID
skilz remove anthropics/web-artifacts-builder

# Remove project-level skill
skilz remove my-skill --project
```

## Working with Registries

### Default Registry Locations

Skilz searches for registries in order:

1. **Project Registry**: `.skilz/registry.yaml` (highest priority)
2. **User Registry**: `~/.skilz/registry.yaml`

### Creating a Custom Registry

Create a `.skilz/registry.yaml` file:

```yaml
# My custom skills
my-org/custom-skill:
  git_repo: https://github.com/my-org/skills-repo
  skill_path: /main/custom-skill
  git_sha: 1234567890abcdef1234567890abcdef12345678

# Override a public skill
anthropics/web-artifacts-builder:
  git_repo: https://github.com/my-fork/claude-code-skills
  skill_path: /main/skills/web-artifacts-builder
  git_sha: abcdef1234567890abcdef1234567890abcdef12
```

### Registry Format

```yaml
<skill-id>:
  git_repo: <git-url>        # Git repository URL
  skill_path: <path>         # Path within repo (/<branch>/path/to/skill)
  git_sha: <sha>             # Exact commit SHA (40 chars)
```

## Project-Level vs User-Level Installation

### User-Level (Default)

Skills installed to user directory:
- Claude Code: `~/.claude/skills/`
- OpenCode: `~/.config/opencode/skills/`

```bash
skilz install anthropics/web-artifacts-builder
# → ~/.claude/skills/web-artifacts-builder/
```

### Project-Level

Skills installed to project directory:
- Claude Code: `.claude/skills/`
- OpenCode: `.opencode/skills/`

```bash
skilz install my-skill --project
# → ./.claude/skills/my-skill/
```

**Use Cases:**
- **User-level**: General-purpose skills you use everywhere
- **Project-level**: Project-specific skills or testing

## Common Workflows

### Setting Up a New Project

```bash
# Create project registry
mkdir -p .skilz
cat > .skilz/registry.yaml <<EOF
my-org/project-skill:
  git_repo: https://github.com/my-org/skills
  skill_path: /main/project-skill
  git_sha: abc123...
EOF

# Install project-level skill
skilz install my-org/project-skill --project

# Verify installation
skilz list --project
```

### Updating All Skills

```bash
# Check what would be updated
skilz update --dry-run

# Update all
skilz update

# Verify updates
skilz list
```

### Managing Multiple Agents

```bash
# Install for Claude Code
skilz install my-skill --agent claude

# Install for OpenCode
skilz install my-skill --agent opencode

# List skills per agent
skilz list --agent claude
skilz list --agent opencode
```

## Troubleshooting

### Skill Not Found

```
Error: Skill 'my-skill' not found in registry.
Searched: ./.skilz/registry.yaml, ~/.skilz/registry.yaml
```

**Solution:** Add the skill to one of the registry files.

### Git Clone Failed

```
Error: Git clone failed: Failed to clone 'https://github.com/...'
Check that the repository URL is correct and you have access.
```

**Solutions:**
- Verify the `git_repo` URL in registry
- Check network connectivity
- Ensure SSH keys are configured (for SSH URLs)
- Use HTTPS URLs for public repos

### Permission Denied

```
Error: Permission denied: /Users/you/.claude/skills/...
```

**Solution:** Check directory permissions or use `sudo` (not recommended).

### Commit SHA Not Found

```
Error: Git checkout failed: Commit 'abc123...' not found in repository.
The registry may reference a commit that doesn't exist or hasn't been fetched.
```

**Solutions:**
- Verify the `git_sha` in registry is correct
- Repository may have been force-pushed
- Update registry with current SHA

## Next Steps

- [Architecture Overview](./03-architecture-overview.md) - Understand how Skilz works
- [Core Modules](../01_core_modules/) - Deep dive into implementation
- [Workflows](../03_workflows/) - Detailed workflow documentation
- [User Manual](../../USER_MANUAL.md) - Complete user guide

---

**[skillzwave.ai](https://skillzwave.ai)** — The largest agent and agent skills marketplace
**[Spillwave](https://spillwave.com)** — Leaders in agentic software development
