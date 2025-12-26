# Changelog

All notable changes to Skilz CLI will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.2] - 2025-01-15

### Added

- **14 AI Agent Support**: Full support for Claude Code, OpenAI Codex, OpenCode CLI, Gemini CLI, GitHub Copilot, Cursor, Aider, Windsurf, Qwen CLI, Kimi CLI, Crush, Plandex, Zed AI, and Universal
- **Universal Skills Directory**: Central skill storage at `~/.skilz/skills/` for sharing across agents
- **Copy vs Symlink Modes**: Choose between copying skills (works everywhere) or symlinking (saves disk space)
- **Config File Sync**: Automatic injection of skill references into agent config files (GEMINI.md, CLAUDE.md, etc.) following [agentskills.io](https://agentskills.io) standard
- **`skilz read` Command**: Load skill content for agents without native skill support
- **User-Level Installation**: Install skills once, use everywhere (for supported agents)
- **Project-Level Installation**: Install skills per-project for workspace-sandboxed agents
- **Comprehensive User Guide**: Detailed documentation for all 14 agents and workflows

### Changed

- **Default Mode for Sandboxed Agents**: Agents without native skill support (Gemini, Copilot, etc.) now default to `--copy` mode instead of `--symlink` to ensure compatibility with workspace sandboxing
- **Config File Detection**: Only updates existing config files; creates primary config file only when needed

### Fixed

- **Symlink Resolution**: Correctly resolve symlinks when reading skills
- **Config File Creation**: Prevent creating secondary config files (e.g., CONTEXT.md for Qwen) when only primary is needed

## [1.0.1] - 2025-01-10

### Added

- `skilz list` command with status checking (up-to-date, outdated, newer)
- `skilz update` command with dry-run support
- `skilz remove` command with confirmation prompts
- JSON output format for scripting
- Project-level installation with `--project` flag

### Changed

- Improved error messages with actionable suggestions
- Better manifest file handling

## [1.0.0] - 2025-01-05

### Added

- Initial release
- `skilz install` command for installing skills from Git repositories
- Registry-based skill resolution
- Claude Code support (`~/.claude/skills/`)
- OpenCode support (`~/.config/opencode/skills/`)
- Manifest file generation for tracking installed skills
- Version pinning via Git SHA
