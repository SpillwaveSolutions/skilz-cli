# Key Project Facts

Critical information about the Skilz CLI project that agents need to remember.

---

## Project Identity

| Fact | Value |
|------|-------|
| **Project Name** | Skilz CLI |
| **Repository** | github.com/spillwave/skilz-cli |
| **Primary Language** | Python 3.10+ |
| **Package Manager** | Poetry |
| **Task Runner** | Taskfile (Go-based) |
| **Test Framework** | pytest |
| **Test Coverage** | 92%+ |

---

## Development Environment

### Required Tools
- Python 3.10+
- Poetry
- Task (optional but recommended)
- Git

### Key Commands
```bash
task test          # Run all tests
task check         # Full quality checks (lint, typecheck, test)
task coverage      # Tests with coverage report
task lint          # Run ruff linter
task typecheck     # Run mypy
```

---

## Architecture Facts

### Skill Installation Flow
1. Parse skill ID from user input
2. Look up in registry (`.skilz/registry.yaml` or `~/.skilz/registry.yaml`)
3. Clone/fetch Git repository to cache
4. Checkout pinned SHA
5. Copy skill files to agent's skill directory
6. Write manifest file

### Supported Agents
| Agent | Skill Directory |
|-------|-----------------|
| Claude Code | `~/.claude/skills/` or `.claude/skills/` |
| OpenCode | `~/.config/opencode/skills/` |

---

## Version Management

**Single Source of Truth:** `pyproject.toml` line 7

| File | Role |
|------|------|
| `pyproject.toml` | Primary version definition (edit this one) |
| `src/skilz/__init__.py` | Dynamic detection via `importlib.metadata.version("skilz")` |

**Release Process:** Only update `pyproject.toml`. The Python module automatically reads the version from package metadata at runtime.

**Previous Bug (Fixed in 1.7):** Before dynamic detection, version was hardcoded in both files and they would get out of sync, causing `skilz --version` to show wrong version.

---

## Important Paths

| Path | Purpose |
|------|---------|
| `src/skilz/` | Main package source |
| `tests/` | Test suite |
| `.skilz/` | Skill templates |
| `.specify/` | SDD specifications |
| `.speckit/` | Spec-kit configuration |
| `docs/project_notes/` | Project memory (THIS FILE) |

---

## Current Status

### Completed Phases
- Phase 1: Core Installer (registry, install, manifest)
- Phase 2: Developer Experience (92% coverage, docs, Taskfile)

### In Progress
- Phase 3: Plugin Support (marketplace.json, extended registry)

### Planned
- Phase 4: Additional agents (Cursor, Codex, Gemini)
- Phase 5: Symlink mode for local development

---

## Integration Points

### SDD (Spec-Driven Development)
- Specs in `.specify/` directory
- Use `/sdd` skill for spec workflows
- All features should have specs before implementation

### JIRA Integration
- Tickets tracked in JIRA
- Use `/jira` skill for ticket operations
- Architect agent manages ticket lifecycle

---

## Quality Gates

Before any PR:
1. `task check` must pass
2. Coverage must stay at 92%+
3. All new features need tests
4. Documentation updated if applicable

---

## Verification History

### 2026-01-21 - v1.9.0 Pre-Release
- ✅ Version bumped to 1.9.0 in pyproject.toml
- ✅ Documentation updated (USER_MANUAL.md, DEPLOY_PYPI.md)
- ✅ CHANGELOG.md updated with 1.9.0 entry
- ✅ All tests passing
- ✅ Local build verified

### 2025-01-09 - v1.8.0 Release
- ✅ List command enhancements (Agent column, --all flag)
- ✅ CLI help discoverability improvements
- ✅ Visit command URL format fix

### 2025-01-08 - v1.7.0 Release
- ✅ Gemini CLI native support
- ✅ NEW/LEGACY/SLUG format support
- ✅ Universal agent custom config

---

*Last Updated: 2026-01-21*
