# Project Summary

## Overview

**Skilz** is a universal package manager for AI skills that works like npm for JavaScript or pip for Python, but specifically designed for AI coding assistants such as Claude Code and OpenCode.

**Browse skills:** [skillzwave.ai](https://skillzwave.ai) — The largest agent and agent skills marketplace
**Built by:** [Spillwave](https://spillwave.com) — Leaders in agentic software development

## Problem Statement

AI coding assistants use "skills" to extend their capabilities. Currently:
- Skills are scattered across repositories
- No standardized installation process
- No version management
- Manual installation is error-prone
- No central registry

## Solution

Skilz provides:
- **Centralized Registry**: YAML-based registry with skill definitions
- **Git SHA Pinning**: Exact version control using git commit SHAs
- **Multi-Agent Support**: Works with Claude Code and OpenCode
- **Idempotent Installation**: Safe to re-run, won't duplicate
- **Project & User Level**: Install globally or per-project
- **Manifest Tracking**: Each skill has `.skilz-manifest.yaml` for tracking

## Key Features

### 1. Registry-Based Installation

```yaml
# .skilz/registry.yaml
anthropics/web-artifacts-builder:
  git_repo: https://github.com/anthropics/claude-code-skills
  skill_path: /main/skills/web-artifacts-builder
  git_sha: a1b2c3d4e5f6...
```

### 2. Simple CLI

```bash
# Install a skill
skilz install anthropics/web-artifacts-builder

# List installed skills
skilz list

# Update skills
skilz update

# Remove a skill
skilz remove web-artifacts-builder
```

### 3. Automatic Agent Detection

Skilz automatically detects whether you're using Claude Code or OpenCode by checking for:
- `.claude/` directory (project-level)
- `~/.claude/` (user-level Claude Code)
- `~/.config/opencode/` (OpenCode)

### 4. Git Caching

- Cloned repositories cached in `~/.skilz/cache`
- Incremental fetches for faster updates
- SHA-based checkout for exact versions

### 5. Manifest Tracking

Each installed skill gets a `.skilz-manifest.yaml`:

```yaml
installed_at: '2025-12-14T20:00:00+00:00'
skill_id: anthropics/web-artifacts-builder
git_repo: https://github.com/anthropics/claude-code-skills
skill_path: /main/skills/web-artifacts-builder
git_sha: a1b2c3d4e5f6789012345678901234567890abcd
skilz_version: 0.1.0
```

## Architecture Principles

### 1. Separation of Concerns

- **CLI Layer**: Argument parsing and command dispatch
- **Commands Layer**: Command implementations
- **Core Layer**: Business logic (installer, scanner, registry, git_ops)
- **Support Layer**: Shared utilities (agents, manifest, errors)

### 2. Spec-Driven Development

The project follows GitHub Spec-Kit methodology:
- `constitution.md` - Project principles
- Feature specs in `.speckit/features/`
- Each feature has: `specify.md`, `plan.md`, `tasks.md`

### 3. Type Safety

- Type hints on all public APIs
- Literal types for agent names
- Dataclasses for structured data
- Mypy for static type checking

### 4. Error Handling

Custom exception hierarchy:
- `SkilzError` - Base exception
- `SkillNotFoundError` - Skill not in registry
- `RegistryError` - Registry loading/parsing errors
- `GitError` - Git operation failures
- `InstallError` - Installation failures

### 5. Testability

- 85%+ code coverage
- Unit tests for all modules
- Integration tests for workflows
- 448 test cases

## Project Structure

```
skilz-cli/
├── src/skilz/              # Source code
│   ├── __init__.py         # Package initialization
│   ├── __main__.py         # Entry point
│   ├── cli.py              # CLI parser and dispatcher
│   ├── commands/           # Command implementations
│   │   ├── install_cmd.py
│   │   ├── list_cmd.py
│   │   ├── update_cmd.py
│   │   └── remove_cmd.py
│   ├── installer.py        # Core installation logic
│   ├── registry.py         # Registry loading
│   ├── scanner.py          # Installed skill discovery
│   ├── git_ops.py          # Git operations
│   ├── agents.py           # Agent detection
│   ├── manifest.py         # Manifest I/O
│   └── errors.py           # Custom exceptions
├── tests/                  # Test suite (92% coverage)
├── .speckit/               # SDD specifications
│   ├── constitution.md
│   └── features/
│       ├── 01-core-installer/
│       ├── 02-skill-management/
│       ├── 03-developer-experience/
│       └── 04-scripting-support/
├── .skilz/                 # Test registry
├── docs/                   # Documentation
├── pyproject.toml          # Project metadata
└── Taskfile.yml            # Build automation
```

## Development Phases

### Phase 1: Core Installer (COMPLETE)
- `skilz install` command
- Registry resolution
- Git cloning and checkout
- Manifest generation
- Claude Code + OpenCode support

### Phase 2: Skill Management (COMPLETE)
- `skilz list` - Show installed skills with status
- `skilz update` - Update to registry versions
- `skilz remove` - Uninstall skills

### Phase 3: Developer Experience (COMPLETE)
- Test coverage 85%+ (target 80%)
- Taskfile.yml automation
- Documentation (README, USER_MANUAL)
- PyPI publishing (`pip install skilz`)

### Phase 4-5: Distribution & Local Install (COMPLETE)
- PyPI publishing: [pypi.org/project/skilz](https://pypi.org/project/skilz/)
- Local skill installation (`skilz install -f /path`)

### Phase 6-7: Multi-Agent Support (COMPLETE)
- 22+ AI agent support from AGENTS.md ecosystem
- Universal skills directory
- Config file sync

## Technology Stack

| Component | Technology |
|-----------|-----------|
| Language | Python 3.10+ |
| CLI Framework | argparse (stdlib) |
| YAML Parsing | PyYAML |
| VCS | Git (subprocess) |
| Build Tool | Hatchling |
| Task Runner | Task (Taskfile.yml) |
| Testing | pytest, pytest-cov |
| Type Checking | mypy |
| Linting | ruff |

## Target Users

1. **AI Coding Assistant Users**: Install and manage skills
2. **Skill Developers**: Publish skills to registries
3. **Enterprise Teams**: Curate private skill registries
4. **CI/CD Pipelines**: Automate skill deployment

## Future Roadmap

- **Public Registry**: Central skill repository
- **Skill Templates**: Scaffolding for new skills
- **Dependency Resolution**: Skills depending on other skills
- **Version Constraints**: Semantic versioning support
- **Skill Marketplace**: Browse and discover skills
- **Plugin System**: Extend skilz functionality

## Links

- **Marketplace:** [skillzwave.ai](https://skillzwave.ai) — Browse and discover skills
- **Company:** [Spillwave](https://spillwave.com) — Leaders in agentic software development
- **PyPI:** [pypi.org/project/skilz](https://pypi.org/project/skilz/) — Install with `pip install skilz`
- [Architecture Overview](./03-architecture-overview.md)
- [Quick Start Guide](./02-quick-start.md)
- [User Manual](../../USER_MANUAL.md)
- [GitHub Repository](https://github.com/spillwave/skilz-cli)
